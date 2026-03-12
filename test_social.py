from app import create_app
from app.models import db, User, FriendRequest, Friendship

app = create_app()

def test_social():
    with app.app_context():
        # Get two test users
        v = User.query.filter_by(email='vaibhav.b-29@scds.saiuniversity.edu.in').first()
        s = User.query.filter_by(email='sharanpranav.a-29@scds.saiuniversity.edu.in').first()
        
        if not v or not s:
            print("Users not found")
            return
            
        print(f"Testing social between {v.name} and {s.name}")
        
        # 1. Clean up existing
        Friendship.query.filter(
            ((Friendship.user1_id == v.id) & (Friendship.user2_id == s.id)) |
            ((Friendship.user1_id == s.id) & (Friendship.user2_id == v.id))
        ).delete()
        FriendRequest.query.filter(
            ((FriendRequest.sender_id == v.id) & (FriendRequest.recipient_id == s.id)) |
            ((FriendRequest.sender_id == s.id) & (FriendRequest.recipient_id == v.id))
        ).delete()
        db.session.commit()
        
        # 2. Test send
        req = FriendRequest(sender_id=v.id, recipient_id=s.id)
        db.session.add(req)
        db.session.commit()
        print("Request sent")
        
        # 3. Verify helper properties
        v = User.query.get(v.id)
        s = User.query.get(s.id)
        print(f"V sent requests: {len(v.sent_requests)}")
        print(f"S pending requests: {len(s.pending_requests)}")
        
        # 4. Test accept
        friendship = Friendship(user1_id=req.sender_id, user2_id=req.recipient_id)
        db.session.add(friendship)
        db.session.delete(req)
        db.session.commit()
        print("Request accepted")
        
        # 5. Verify friendship
        v = User.query.get(v.id)
        s = User.query.get(s.id)
        print(f"V friends: {len(v.friends)}")
        print(f"S friends: {len(s.friends)}")
        print(f"V is friends with S? {v.is_friends_with(s.id)}")

if __name__ == "__main__":
    test_social()
