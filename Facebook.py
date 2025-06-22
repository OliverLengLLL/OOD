from datetime import datetime
from typing import List, Dict, Optional, Set
from enum import Enum
import uuid

# Enums for better type safety
class PostType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"

class FriendshipStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"

class NotificationType(Enum):
    FRIEND_REQUEST = "friend_request"
    POST_LIKE = "post_like"
    POST_COMMENT = "post_comment"

# Core Entity Classes
class User:
    def __init__(self, user_id: str, email: str, name: str, password: str):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.password = password  # In real system, this would be hashed
        self.profile_picture: Optional[str] = None
        self.bio: Optional[str] = None
        self.created_at = datetime.now()
        self.is_active = True
        
    def update_profile(self, name: str = None, bio: str = None, profile_picture: str = None):
        if name:
            self.name = name
        if bio:
            self.bio = bio
        if profile_picture:
            self.profile_picture = profile_picture

class Post:
    def __init__(self, post_id: str, author_id: str, content: str, post_type: PostType):
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.post_type = post_type
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = True
        self.privacy_level = "public"  # public, friends, private
        
    def update_content(self, content: str):
        self.content = content
        self.updated_at = datetime.now()

class Comment:
    def __init__(self, comment_id: str, post_id: str, author_id: str, content: str):
        self.comment_id = comment_id
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.created_at = datetime.now()
        self.is_active = True

class Like:
    def __init__(self, like_id: str, post_id: str, user_id: str):
        self.like_id = like_id
        self.post_id = post_id
        self.user_id = user_id
        self.created_at = datetime.now()

class Friendship:
    def __init__(self, friendship_id: str, requester_id: str, receiver_id: str):
        self.friendship_id = friendship_id
        self.requester_id = requester_id
        self.receiver_id = receiver_id
        self.status = FriendshipStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def accept(self):
        self.status = FriendshipStatus.ACCEPTED
        self.updated_at = datetime.now()
        
    def block(self):
        self.status = FriendshipStatus.BLOCKED
        self.updated_at = datetime.now()

class Notification:
    def __init__(self, notification_id: str, user_id: str, message: str, notification_type: NotificationType):
        self.notification_id = notification_id
        self.user_id = user_id
        self.message = message
        self.notification_type = notification_type
        self.is_read = False
        self.created_at = datetime.now()
        
    def mark_as_read(self):
        self.is_read = True

# Service Layer Classes
class UserService:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.email_to_user_id: Dict[str, str] = {}
        
    def create_user(self, email: str, name: str, password: str) -> User:
        if email in self.email_to_user_id:
            raise ValueError("User with this email already exists")
            
        user_id = str(uuid.uuid4())
        user = User(user_id, email, name, password)
        self.users[user_id] = user
        self.email_to_user_id[email] = user_id
        return user
        
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
        
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user_id = self.email_to_user_id.get(email)
        if user_id:
            user = self.users[user_id]
            if user.password == password and user.is_active:
                return user
        return None
        
    def search_users(self, query: str) -> List[User]:
        results = []
        query_lower = query.lower()
        for user in self.users.values():
            if (query_lower in user.name.lower() or 
                query_lower in user.email.lower()) and user.is_active:
                results.append(user)
        return results

class PostService:
    def __init__(self):
        self.posts: Dict[str, Post] = {}
        self.user_posts: Dict[str, List[str]] = {}  # user_id -> list of post_ids
        
    def create_post(self, author_id: str, content: str, post_type: PostType) -> Post:
        post_id = str(uuid.uuid4())
        post = Post(post_id, author_id, content, post_type)
        
        self.posts[post_id] = post
        if author_id not in self.user_posts:
            self.user_posts[author_id] = []
        self.user_posts[author_id].append(post_id)
        
        return post
        
    def get_post(self, post_id: str) -> Optional[Post]:
        return self.posts.get(post_id)
        
    def get_user_posts(self, user_id: str) -> List[Post]:
        post_ids = self.user_posts.get(user_id, [])
        return [self.posts[post_id] for post_id in post_ids if self.posts[post_id].is_active]
        
    def delete_post(self, post_id: str, user_id: str) -> bool:
        post = self.posts.get(post_id)
        if post and post.author_id == user_id:
            post.is_active = False
            return True
        return False

class CommentService:
    def __init__(self):
        self.comments: Dict[str, Comment] = {}
        self.post_comments: Dict[str, List[str]] = {}  # post_id -> list of comment_ids
        
    def add_comment(self, post_id: str, author_id: str, content: str) -> Comment:
        comment_id = str(uuid.uuid4())
        comment = Comment(comment_id, post_id, author_id, content)
        
        self.comments[comment_id] = comment
        if post_id not in self.post_comments:
            self.post_comments[post_id] = []
        self.post_comments[post_id].append(comment_id)
        
        return comment
        
    def get_post_comments(self, post_id: str) -> List[Comment]:
        comment_ids = self.post_comments.get(post_id, [])
        return [self.comments[cid] for cid in comment_ids if self.comments[cid].is_active]

class LikeService:
    def __init__(self):
        self.likes: Dict[str, Like] = {}
        self.post_likes: Dict[str, Set[str]] = {}  # post_id -> set of user_ids
        self.user_likes: Dict[str, Set[str]] = {}  # user_id -> set of post_ids
        
    def add_like(self, post_id: str, user_id: str) -> Optional[Like]:
        if post_id in self.post_likes and user_id in self.post_likes[post_id]:
            return None  # Already liked
            
        like_id = str(uuid.uuid4())
        like = Like(like_id, post_id, user_id)
        
        self.likes[like_id] = like
        
        if post_id not in self.post_likes:
            self.post_likes[post_id] = set()
        self.post_likes[post_id].add(user_id)
        
        if user_id not in self.user_likes:
            self.user_likes[user_id] = set()
        self.user_likes[user_id].add(post_id)
        
        return like
        
    def remove_like(self, post_id: str, user_id: str) -> bool:
        if (post_id in self.post_likes and user_id in self.post_likes[post_id]):
            self.post_likes[post_id].remove(user_id)
            self.user_likes[user_id].remove(post_id)
            return True
        return False
        
    def get_post_like_count(self, post_id: str) -> int:
        return len(self.post_likes.get(post_id, set()))
        
    def has_user_liked_post(self, post_id: str, user_id: str) -> bool:
        return post_id in self.post_likes and user_id in self.post_likes[post_id]

class FriendshipService:
    def __init__(self):
        self.friendships: Dict[str, Friendship] = {}
        self.user_friendships: Dict[str, Dict[str, str]] = {}  # user_id -> {friend_id: friendship_id}
        
    def send_friend_request(self, requester_id: str, receiver_id: str) -> Optional[Friendship]:
        if requester_id == receiver_id:
            return None
            
        # Check if friendship already exists
        if (requester_id in self.user_friendships and 
            receiver_id in self.user_friendships[requester_id]):
            return None
            
        friendship_id = str(uuid.uuid4())
        friendship = Friendship(friendship_id, requester_id, receiver_id)
        
        self.friendships[friendship_id] = friendship
        
        # Update mappings for both users
        if requester_id not in self.user_friendships:
            self.user_friendships[requester_id] = {}
        if receiver_id not in self.user_friendships:
            self.user_friendships[receiver_id] = {}
            
        self.user_friendships[requester_id][receiver_id] = friendship_id
        self.user_friendships[receiver_id][requester_id] = friendship_id
        
        return friendship
        
    def accept_friend_request(self, friendship_id: str, user_id: str) -> bool:
        friendship = self.friendships.get(friendship_id)
        if friendship and friendship.receiver_id == user_id:
            friendship.accept()
            return True
        return False
        
    def get_friends(self, user_id: str) -> List[str]:
        friends = []
        if user_id in self.user_friendships:
            for friend_id, friendship_id in self.user_friendships[user_id].items():
                friendship = self.friendships[friendship_id]
                if friendship.status == FriendshipStatus.ACCEPTED:
                    friends.append(friend_id)
        return friends
        
    def are_friends(self, user1_id: str, user2_id: str) -> bool:
        if user1_id in self.user_friendships and user2_id in self.user_friendships[user1_id]:
            friendship_id = self.user_friendships[user1_id][user2_id]
            friendship = self.friendships[friendship_id]
            return friendship.status == FriendshipStatus.ACCEPTED
        return False

class FeedService:
    def __init__(self, post_service: PostService, friendship_service: FriendshipService):
        self.post_service = post_service
        self.friendship_service = friendship_service
        
    def get_user_feed(self, user_id: str, limit: int = 20) -> List[Post]:
        # Get user's friends
        friends = self.friendship_service.get_friends(user_id)
        friends.append(user_id)  # Include user's own posts
        
        # Collect all posts from friends
        all_posts = []
        for friend_id in friends:
            friend_posts = self.post_service.get_user_posts(friend_id)
            all_posts.extend(friend_posts)
            
        # Sort by creation time (newest first) and limit
        all_posts.sort(key=lambda x: x.created_at, reverse=True)
        return all_posts[:limit]

# Main Facebook System Class
class FacebookSystem:
    def __init__(self):
        self.user_service = UserService()
        self.post_service = PostService()
        self.comment_service = CommentService()
        self.like_service = LikeService()
        self.friendship_service = FriendshipService()
        self.feed_service = FeedService(self.post_service, self.friendship_service)
        
    # User operations
    def register_user(self, email: str, name: str, password: str) -> User:
        return self.user_service.create_user(email, name, password)
        
    def login(self, email: str, password: str) -> Optional[User]:
        return self.user_service.authenticate_user(email, password)
        
    # Post operations
    def create_post(self, user_id: str, content: str, post_type: PostType = PostType.TEXT) -> Post:
        return self.post_service.create_post(user_id, content, post_type)
        
    def like_post(self, post_id: str, user_id: str) -> bool:
        like = self.like_service.add_like(post_id, user_id)
        return like is not None
        
    def unlike_post(self, post_id: str, user_id: str) -> bool:
        return self.like_service.remove_like(post_id, user_id)
        
    def comment_on_post(self, post_id: str, user_id: str, content: str) -> Comment:
        return self.comment_service.add_comment(post_id, user_id, content)
        
    # Friend operations
    def send_friend_request(self, requester_id: str, receiver_id: str) -> bool:
        friendship = self.friendship_service.send_friend_request(requester_id, receiver_id)
        return friendship is not None
        
    def accept_friend_request(self, friendship_id: str, user_id: str) -> bool:
        return self.friendship_service.accept_friend_request(friendship_id, user_id)
        
    # Feed operations
    def get_user_feed(self, user_id: str, limit: int = 20) -> List[Post]:
        return self.feed_service.get_user_feed(user_id, limit)
        
    # Search operations
    def search_users(self, query: str) -> List[User]:
        return self.user_service.search_users(query)