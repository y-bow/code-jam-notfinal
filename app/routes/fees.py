from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from ..models import db, Fee, FeePayment, User
from ..permissions import (
    require_role, require_min_role, student_required, 
    dean_required, admin_required, school_scope
)
import uuid

fees_bp = Blueprint('fees', __name__, url_prefix='/fees')

@fees_bp.route('/student')
@student_required
def student_dashboard():
    user = g.current_user
    # Fee is linked to User (student)
    fee = Fee.query.filter_by(student_id=user.id).first()
    
    if not fee:
        # Create a blank fee profile if none exists for this student
        fee = Fee(student_id=user.id, tuition_fee=0, lab_fee=0, library_fee=0, exam_fee=0, other_charges=0)
        db.session.add(fee)
        db.session.commit()
        
    payments = FeePayment.query.filter_by(fee_id=fee.id).order_by(FeePayment.payment_date.desc()).all()
    
    return render_template('fees/student_dashboard.html', fee=fee, payments=payments)

@fees_bp.route('/pay', methods=['GET', 'POST'])
@student_required
def process_payment():
    user = g.current_user
    fee = Fee.query.filter_by(student_id=user.id).first()
    
    if not fee or fee.remaining_balance <= 0:
        flash("No pending fees to pay.", "info")
        return redirect(url_for('fees.student_dashboard'))
        
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
        except ValueError:
            amount = 0
            
        method = request.form.get('payment_method')
        
        if amount <= 0 or amount > fee.remaining_balance:
            flash("Invalid payment amount.", "error")
            return redirect(url_for('fees.process_payment'))
            
        if not method:
            flash("Please select a payment method.", "error")
            return redirect(url_for('fees.process_payment'))
            
        # Simulate payment processing
        txn_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
        payment = FeePayment(
            fee_id=fee.id,
            amount=amount,
            payment_method=method,
            status='success',  # Assuming success for dummy gateway
            transaction_id=txn_id
        )
        db.session.add(payment)
        db.session.commit()
        
        flash(f"Payment of ₹{amount:,.0f} successful! Transaction ID: {txn_id}", "success")
        return redirect(url_for('fees.student_dashboard'))
        
    return render_template('fees/payment_gateway.html', fee=fee)

@fees_bp.route('/receipt/<int:payment_id>')
@require_min_role('student')
def print_receipt(payment_id):
    payment = FeePayment.query.get_or_404(payment_id)
    user = g.current_user
    
    # Security check:
    # 1. Platform owner can see any receipt
    # 2. Staff can see any receipt in their school
    # 3. Student can only see their own receipt
    
    can_access = False
    if user.role == 'platform_owner':
        can_access = True
    elif user.role in ('admin', 'dean'):
        # Check if student belongs to same school
        if payment.fee.student.school_id == g.school_id:
            can_access = True
    elif payment.fee.student_id == user.id:
        can_access = True
        
    if not can_access:
        abort(403)
        
    return render_template('fees/receipt.html', payment=payment, student=payment.fee.student)

@fees_bp.route('/admin')
@require_min_role('dean')
def admin_dashboard():
    user = g.current_user
        
    # Get students and their fees
    if user.role == 'platform_owner':
        students = User.query.filter_by(role='student').all()
        fees = Fee.query.all()
        recent_payments = FeePayment.query.order_by(FeePayment.payment_date.desc()).limit(20).all()
    else:
        students = User.query.filter_by(school_id=g.school_id, role='student').all()
        fees = (
            Fee.query
            .join(User, Fee.student_id == User.id)
            .filter(User.school_id == g.school_id)
            .all()
        )
        recent_payments = (
            FeePayment.query
            .join(Fee)
            .join(User, Fee.student_id == User.id)
            .filter(User.school_id == g.school_id)
            .order_by(FeePayment.payment_date.desc())
            .limit(10)
            .all()
        )
    
    total_expected = sum(f.total_amount for f in fees)
    total_collected = sum(f.amount_paid for f in fees)
    
    return render_template('fees/admin_dashboard.html', 
                          students=students, 
                          fees=fees,
                          total_expected=total_expected, 
                          total_collected=total_collected,
                          recent_payments=recent_payments)

@fees_bp.route('/admin/offline-payment', methods=['POST'])
@require_min_role('dean')
def record_offline_payment():
    user = g.current_user
    student_id = request.form.get('student_id')
    
    # Security: Ensure student belongs to school (unless platform owner)
    student = User.query.get_or_404(student_id)
    if user.role != 'platform_owner' and student.school_id != g.school_id:
        abort(403)
        
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        amount = 0
        
    notes = request.form.get('notes', 'Offline Payment')
    
    fee = Fee.query.filter_by(student_id=student.id).first()
    
    if not fee:
        flash("Student fee record not found.", "error")
    elif amount <= 0:
        flash("Invalid amount.", "error")
    else:
        # Create payment record
        txn_id = f"OFF-{uuid.uuid4().hex[:6].upper()}"
        payment = FeePayment(
            fee_id=fee.id,
            amount=amount,
            payment_method='Offline / Cash',
            status='success',
            notes=notes,
            transaction_id=txn_id
        )
        db.session.add(payment)
        db.session.commit()
        flash(f"Offline payment of ₹{amount:,.0f} recorded for {student.name}.", "success")
        
    return redirect(url_for('fees.admin_dashboard'))
