from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from app.models import db, Fee, FeePayment, User
from app.middleware import school_scoped, role_minimum
import uuid

fees_bp = Blueprint('fees', __name__, url_prefix='/fees')

@fees_bp.route('/student')
@school_scoped
def student_dashboard():
    if g.current_user.role != 'student':
        flash("Unauthorized access.", "error")
        return redirect(url_for('dashboard.teacher_dashboard'))
        
    user_id = g.current_user.id
    fee = Fee.query.filter_by(student_id=user_id).first()
    
    if not fee:
        # Create a blank fee profile if none exists for this student
        fee = Fee(student_id=user_id, tuition_fee=0, lab_fee=0, library_fee=0, exam_fee=0, other_charges=0)
        db.session.add(fee)
        db.session.commit()
        
    payments = FeePayment.query.filter_by(fee_id=fee.id).order_by(FeePayment.payment_date.desc()).all()
    
    return render_template('fees/student_dashboard.html', fee=fee, payments=payments)

@fees_bp.route('/pay', methods=['GET', 'POST'])
@school_scoped
def process_payment():
    if g.current_user.role != 'student':
        flash("Unauthorized access.", "error")
        return redirect(url_for('dashboard.teacher_dashboard'))
        
    user_id = g.current_user.id
    fee = Fee.query.filter_by(student_id=user_id).first()
    
    if not fee or fee.remaining_balance <= 0:
        flash("No pending fees to pay.", "info")
        return redirect(url_for('fees.student_dashboard'))
        
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
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
@school_scoped
def print_receipt(payment_id):
    payment = FeePayment.query.get_or_404(payment_id)
    user_id = g.current_user.id
    
    # Security check: only the student who owns the payment, or administration roles, can view the receipt
    is_admin = g.current_user.role in ['admin', 'dean']
    if not is_admin and payment.fee.student_id != user_id:
        flash("Unauthorized.", "error")
        return redirect(url_for('fees.student_dashboard'))
        
    return render_template('fees/receipt.html', payment=payment, student=payment.fee.student)

@fees_bp.route('/admin')
@school_scoped
@role_minimum('dean')
def admin_dashboard():
        
    # Get students and their fees (Global Admin sees all, Dean sees school-only)
    if g.current_user.role == 'admin':
        students = User.query.filter_by(role='student').all()
        fees = Fee.query.all()
        recent_payments = FeePayment.query.order_by(FeePayment.payment_date.desc()).limit(20).all()
    else:
        students = User.query.filter_by(school_id=g.school_id, role='student').all()
        # Assuming Fee model has a relationship or we need to join with User
        # If Fee doesn't have school_id, we join with User
        fees = Fee.query.join(User).filter(User.school_id == g.school_id).all()
        recent_payments = FeePayment.query.join(Fee).join(User).filter(User.school_id == g.school_id).order_by(FeePayment.payment_date.desc()).limit(10).all()
    
    total_expected = sum(f.total_amount for f in fees)
    total_collected = sum(f.amount_paid for f in fees)
    
    return render_template('fees/admin_dashboard.html', 
                          students=students, 
                          fees=fees,
                          total_expected=total_expected, 
                          total_collected=total_collected,
                          recent_payments=recent_payments)

@fees_bp.route('/admin/offline-payment', methods=['POST'])
@school_scoped
def record_offline_payment():
    if g.current_user.role not in ['admin', 'dean']:
        return "Unauthorized", 403
        
    student_id = request.form.get('student_id')
    amount = float(request.form.get('amount', 0))
    notes = request.form.get('notes', 'Offline Payment')
    
    fee = Fee.query.filter_by(student_id=student_id).first()
    
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
            transaction_id=txn_id
        )
        db.session.add(payment)
        db.session.commit()
        flash(f"Offline payment of ₹{amount:,.0f} recorded for {fee.student.name}.", "success")
        
    return redirect(url_for('fees.admin_dashboard'))
