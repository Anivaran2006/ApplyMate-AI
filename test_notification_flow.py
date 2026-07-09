from app.services.category_service import detect_category
from app.services.user_service import get_matching_users

notice_text = "NEET UG Registration Open"

category = detect_category(notice_text)

users = get_matching_users(category)

print("Category:", category)
print("Users:", users)