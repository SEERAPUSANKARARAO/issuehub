"""
IssueHub — Database Seed Script
=================================
Populates the database with realistic sample data directly via SQLAlchemy.
No server needs to be running. Just run this script once after setup.

Usage:
    cd backend
    python seed.py

    # Reset and re-seed (wipes existing data first)
    python seed.py --reset

    # Preview what will be created without writing to DB
    python seed.py --dry-run
"""

import sys
import os
import argparse
from datetime import datetime, timezone

# ── Make sure we can import the app modules ───────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.db.session import SessionLocal, engine
    from app.db.base import Base
    from app.models.user import User
    from app.models.project import Project
    from app.models.project_member import ProjectMember
    from app.models.issue import Issue
    from app.models.comment import Comment
    from app.core.security import hash_password
except ImportError as e:
    print(f"\n✗ Import error: {e}")
    print("  Make sure you are running this from the backend/ directory:")
    print("  cd backend && python seed.py\n")
    sys.exit(1)

# ── Terminal colors ───────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def log(icon, msg, color=RESET):
    print(f"  {color}{icon} {msg}{RESET}")

def section(title):
    print(f"\n{CYAN}{BOLD}── {title} {'─' * (52 - len(title))}{RESET}")

# ══════════════════════════════════════════════════════════════
# SEED DATA DEFINITIONS
# ══════════════════════════════════════════════════════════════

USERS = [
    {
        "name":     "Arjun Sharma",
        "email":    "arjun@issuehub.dev",
        "password": "arjun1234",
        "role_tag": "Project Lead / Maintainer",
    },
    {
        "name":     "Priya Nair",
        "email":    "priya@issuehub.dev",
        "password": "priya1234",
        "role_tag": "Frontend Developer",
    },
    {
        "name":     "Rahul Verma",
        "email":    "rahul@issuehub.dev",
        "password": "rahul1234",
        "role_tag": "Backend Developer",
    },
    {
        "name":     "Sneha Patel",
        "email":    "sneha@issuehub.dev",
        "password": "sneha1234",
        "role_tag": "QA Engineer",
    },
]

PROJECTS = [
    {
        "name":        "ShopEase E-Commerce",
        "key":         "SHOP",
        "description": "Full-stack e-commerce platform with cart, payments, and order tracking",
        "owner":       "arjun@issuehub.dev",
        "members": [
            ("priya@issuehub.dev", "member"),
            ("rahul@issuehub.dev", "member"),
            ("sneha@issuehub.dev", "member"),
        ],
    },
    {
        "name":        "PayFlow Banking",
        "key":         "PAY",
        "description": "Mobile banking application with transfers, statements, and UPI integration",
        "owner":       "arjun@issuehub.dev",
        "members": [
            ("rahul@issuehub.dev", "member"),
        ],
    },
    {
        "name":        "HRDesk Portal",
        "key":         "HR",
        "description": "Employee management, leave tracking, and payroll processing system",
        "owner":       "arjun@issuehub.dev",
        "members": [
            ("priya@issuehub.dev", "member"),
        ],
    },
]

# Issues keyed by project key
ISSUES = {
    "SHOP": [
        {
            "title":       "Payment gateway timeout on checkout",
            "description": (
                "Users are experiencing a 30-second timeout when completing payment on the checkout page. "
                "The Razorpay callback is not returning within the expected window. "
                "Reproducible on both mobile and desktop. Affects 100% of live transactions.\n\n"
                "Steps to reproduce:\n"
                "1. Add any item to cart\n"
                "2. Proceed to checkout\n"
                "3. Enter card details and click Pay\n"
                "4. Observe timeout after 30 seconds"
            ),
            "priority": "high",
            "status":   "in_progress",
            "reporter": "arjun@issuehub.dev",
            "comments": [
                ("rahul@issuehub.dev",
                 "Reproduced on staging. Razorpay webhook responding correctly but frontend awaiting "
                 "a redirect that never comes. Looks like a missing return URL config in the payment init call."),
                ("priya@issuehub.dev",
                 "Checked the network tab — POST to /api/payments/initiate returns 200 but response body is empty. "
                 "Something wrong server-side before the redirect URL is even constructed."),
                ("arjun@issuehub.dev",
                 "Found it. RAZORPAY_RETURN_URL environment variable not set in production. "
                 "Set to https://shopease.com/payment/callback and redeploy. Pushing the fix now."),
                ("sneha@issuehub.dev",
                 "Verified the fix on staging. Payment completes and redirects to order confirmation. "
                 "Ready for production deploy."),
            ],
        },
        {
            "title":       "Product images not loading on Safari",
            "description": (
                "All product images return a 404 on Safari 17+ (macOS Ventura and iOS 17). "
                "Image URLs contain spaces not being URL-encoded before being sent to the CDN. "
                "Chrome and Firefox unaffected due to automatic encoding.\n\n"
                "Affected: Safari 17.0, Safari 17.1\n"
                "Not affected: Chrome 120, Firefox 121, Edge 120"
            ),
            "priority": "high",
            "status":   "closed",
            "reporter": "priya@issuehub.dev",
            "comments": [
                ("rahul@issuehub.dev",
                 "Confirmed. The image CDN URL builder in imageUtils.js is calling encodeURI() "
                 "instead of encodeURIComponent() — encodeURI skips spaces."),
                ("priya@issuehub.dev",
                 "Fix deployed in v2.3.1. Replaced encodeURI with encodeURIComponent in imageUtils.js line 47. "
                 "Tested on Safari 17.0 and 17.1 — images loading correctly."),
            ],
        },
        {
            "title":       "Search results do not update when filter is cleared",
            "description": (
                "When a user applies a category filter on the product search page and then removes it "
                "by clicking 'Clear Filters', the product list does not re-fetch. "
                "Stale filtered results remain visible until the page is manually refreshed.\n\n"
                "Expected: list refreshes immediately when filter is cleared\n"
                "Actual: stale results persist"
            ),
            "priority": "high",
            "status":   "open",
            "reporter": "rahul@issuehub.dev",
            "comments": [
                ("priya@issuehub.dev",
                 "Found the cause. The useEffect in ProductList.jsx has the filters object as a dependency "
                 "but clearing the filter sets it to null rather than an empty object. "
                 "React sees null !== {} so it skips the effect. Easy fix — normalize to empty object."),
            ],
        },
        {
            "title":       "Add Save to Wishlist button on product cards",
            "description": (
                "Currently users can only save items to wishlist from the product detail page. "
                "Adding a quick-save button directly on the product card in the listing view "
                "would reduce friction and improve conversion rate.\n\n"
                "Acceptance criteria:\n"
                "- Heart icon appears on hover over product card\n"
                "- Clicking saves to wishlist without navigating away\n"
                "- Icon fills when item is already in wishlist\n"
                "- Works for both logged-in and guest users (guest: prompt to login)"
            ),
            "priority": "medium",
            "status":   "open",
            "reporter": "sneha@issuehub.dev",
            "comments": [],
        },
        {
            "title":       "Order confirmation email missing itemized price breakdown",
            "description": (
                "The order confirmation email sent after successful checkout shows only the total amount. "
                "It should include an itemized list showing each product, quantity, unit price, subtotal, "
                "tax, shipping charge, and final total — matching the order summary page format."
            ),
            "priority": "low",
            "status":   "open",
            "reporter": "arjun@issuehub.dev",
            "comments": [],
        },
        {
            "title":       "Duplicate orders created on double-click of Pay button",
            "description": (
                "If a user double-clicks 'Complete Payment', two separate orders are created with "
                "two separate payment attempts. The button is not disabled after the first click.\n\n"
                "Severity: Critical — causes duplicate charges on customer cards\n"
                "Frequency: Reported by 3 customers this week"
            ),
            "priority": "high",
            "status":   "in_progress",
            "reporter": "rahul@issuehub.dev",
            "comments": [
                ("arjun@issuehub.dev",
                 "Confirmed critical. Disabling the Pay button on first click is the immediate fix. "
                 "Also need idempotency key on the payment API to prevent duplicate orders even if two requests slip through."),
                ("rahul@issuehub.dev",
                 "Button disable fix is a one-liner — pushing in 30 minutes. "
                 "Idempotency key will take a few hours. Pushing button fix as hotfix now, idempotency key next sprint."),
                ("arjun@issuehub.dev",
                 "Approved. Push button disable as emergency hotfix. "
                 "Create a separate issue for the idempotency key implementation and link it here."),
            ],
        },
        {
            "title":       "Cart item count badge not visible in dark mode",
            "description": (
                "The red badge showing cart item count on the navbar icon uses red background with white text. "
                "In dark mode the badge blends with the dark navbar and becomes hard to see. "
                "Needs a border or drop shadow for contrast."
            ),
            "priority": "low",
            "status":   "open",
            "reporter": "priya@issuehub.dev",
            "comments": [],
        },
    ],

    "PAY": [
        {
            "title":       "UPI transaction history missing for transfers older than 30 days",
            "description": (
                "The transaction history screen only fetches the last 30 days of UPI transfers. "
                "Users are unable to view or download statements for older transactions. "
                "The API supports a date range parameter but the frontend is not passing it correctly."
            ),
            "priority": "high",
            "status":   "open",
            "reporter": "arjun@issuehub.dev",
            "comments": [
                ("rahul@issuehub.dev",
                 "Confirmed. The fetchTransactions() call in transactionService.js hardcodes "
                 "fromDate = today - 30 days. Need to expose a date picker and pass selected range to API."),
            ],
        },
        {
            "title":       "OTP not received on Airtel numbers",
            "description": (
                "Login OTP is not being delivered to Airtel mobile numbers. "
                "Jio and Vi numbers work correctly. "
                "Issue started appearing after the SMS gateway was switched on 2024-12-01. "
                "Airtel numbers constitute approximately 28% of the user base."
            ),
            "priority": "high",
            "status":   "closed",
            "reporter": "arjun@issuehub.dev",
            "comments": [
                ("rahul@issuehub.dev",
                 "Raised a support ticket with the new SMS gateway. Root cause: Airtel requires "
                 "a DLT-registered sender ID which we did not configure after the gateway switch. "
                 "Configuration updated — OTPs delivering normally as of 2024-12-03 14:30 IST."),
                ("arjun@issuehub.dev",
                 "Verified with 5 Airtel test numbers. OTPs arriving within 10 seconds. Closing this issue."),
            ],
        },
        {
            "title":       "Add biometric authentication support for app login",
            "description": (
                "Users have requested fingerprint and Face ID login as an alternative to PIN entry. "
                "This is now a standard feature in competing banking apps. "
                "Would improve both security and user experience."
            ),
            "priority": "medium",
            "status":   "open",
            "reporter": "rahul@issuehub.dev",
            "comments": [],
        },
    ],

    "HR": [
        {
            "title":       "Leave balance showing incorrect count after half-day approval",
            "description": (
                "When a half-day leave request is approved, the system deducts 1 full day from "
                "the leave balance instead of 0.5 days. Confirmed across multiple employee accounts. "
                "The deduction logic in the leave approval handler is not handling the 'half_day' flag correctly."
            ),
            "priority": "high",
            "status":   "in_progress",
            "reporter": "arjun@issuehub.dev",
            "comments": [
                ("priya@issuehub.dev",
                 "Found the bug in leaveService.js deductLeave(). It uses Math.floor() on the duration "
                 "which rounds 0.5 down to 0 in one branch and hardcodes 1 in another. Clear logic error."),
                ("arjun@issuehub.dev",
                 "Needs to be fixed before payroll cycle on the 1st. Can you take this Priya? "
                 "Also need a correction script for the 14 employees affected this month."),
                ("priya@issuehub.dev",
                 "On it. Fix is straightforward. Will also write a migration script to correct affected "
                 "balances and get Sneha to verify the counts before we run it in production."),
            ],
        },
        {
            "title":       "Employee profile photo upload fails for files above 2MB",
            "description": (
                "The profile photo upload returns a 413 error for files above 2MB "
                "even though the stated limit in the UI is 5MB. "
                "The server-side limit and the UI label are out of sync. "
                "Either raise the server limit to 5MB or correct the UI label."
            ),
            "priority": "medium",
            "status":   "open",
            "reporter": "priya@issuehub.dev",
            "comments": [
                ("arjun@issuehub.dev",
                 "Server limit was set to 2MB in nginx config (client_max_body_size 2m). "
                 "Updating to 5MB and redeploying. UI label was correct — the config was wrong."),
            ],
        },
    ],
}

# ══════════════════════════════════════════════════════════════
# SEED FUNCTIONS
# ══════════════════════════════════════════════════════════════

def reset_db(db):
    """Drop and recreate all tables."""
    log("⚠", "Resetting database — all existing data will be deleted", YELLOW)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    log("✓", "Database reset complete", GREEN)


def seed_users(db, dry_run=False):
    section("Creating Users")
    created = {}
    for u in USERS:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            log("○", f"User already exists: {u['name']} <{u['email']}>", DIM)
            created[u["email"]] = existing
            continue
        if dry_run:
            log("~", f"[DRY RUN] Would create: {u['name']} <{u['email']}> ({u['role_tag']})", YELLOW)
            continue
        user = User(
            name=u["name"],
            email=u["email"],
            password_hash=hash_password(u["password"]),
        )
        db.add(user)
        db.flush()
        created[u["email"]] = user
        log("✓", f"Created user: {u['name']} <{u['email']}> — password: {u['password']}", GREEN)
    return created


def seed_projects(db, user_map, dry_run=False):
    section("Creating Projects & Members")
    created = {}
    for p in PROJECTS:
        existing = db.query(Project).filter(Project.key == p["key"]).first()
        if existing:
            log("○", f"Project already exists: {p['name']} [{p['key']}]", DIM)
            created[p["key"]] = existing
            continue
        if dry_run:
            log("~", f"[DRY RUN] Would create project: {p['name']} [{p['key']}]", YELLOW)
            for email, role in p["members"]:
                log("~", f"  [DRY RUN] Member: {email} ({role})", YELLOW)
            continue

        owner = user_map.get(p["owner"])
        if not owner:
            log("✗", f"Owner not found: {p['owner']}", RED)
            continue

        project = Project(name=p["name"], key=p["key"], description=p["description"])
        db.add(project)
        db.flush()

        # Owner becomes maintainer
        db.add(ProjectMember(project_id=project.id, user_id=owner.id, role="maintainer"))
        log("✓", f"Created project: {p['name']} [{p['key']}] — owner: {owner.name}", GREEN)

        # Add members
        for email, role in p["members"]:
            member_user = user_map.get(email)
            if not member_user:
                log("✗", f"  Member not found: {email}", RED)
                continue
            # Check not already added
            existing_mem = db.query(ProjectMember).filter(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == member_user.id,
            ).first()
            if not existing_mem:
                db.add(ProjectMember(project_id=project.id, user_id=member_user.id, role=role))
                log("✓", f"  Added member: {member_user.name} ({role})", GREEN)

        created[p["key"]] = project
    return created


def seed_issues(db, user_map, project_map, dry_run=False):
    section("Creating Issues & Comments")
    total_issues   = 0
    total_comments = 0

    for proj_key, issue_list in ISSUES.items():
        project = project_map.get(proj_key)
        if not project:
            log("✗", f"Project {proj_key} not found — skipping its issues", RED)
            continue

        print(f"\n  {BOLD}Project: {project.name} [{proj_key}]{RESET}")

        for issue_data in issue_list:
            reporter = user_map.get(issue_data["reporter"])
            if not reporter:
                log("✗", f"Reporter not found: {issue_data['reporter']}", RED)
                continue

            # Check duplicate
            existing = db.query(Issue).filter(
                Issue.project_id == project.id,
                Issue.title == issue_data["title"],
            ).first()

            if existing:
                log("○", f"Issue exists: {issue_data['title'][:55]}...", DIM)
                issue_obj = existing
            elif dry_run:
                log("~", f"[DRY RUN] Would create [{issue_data['priority'].upper()}] "
                         f"[{issue_data['status']}]: {issue_data['title'][:50]}...", YELLOW)
                for c_email, _ in issue_data.get("comments", []):
                    log("~", f"  [DRY RUN] Comment by: {c_email}", YELLOW)
                continue
            else:
                issue_obj = Issue(
                    project_id=issue_data.get("project_id", project.id),
                    title=issue_data["title"],
                    description=issue_data["description"],
                    priority=issue_data["priority"],
                    status=issue_data["status"],
                    reporter_id=reporter.id,
                )
                # Set project_id explicitly
                issue_obj.project_id = project.id
                db.add(issue_obj)
                db.flush()
                total_issues += 1
                log("✓",
                    f"[{issue_data['priority'].upper():6}] [{issue_data['status']:11}] "
                    f"{issue_data['title'][:50]}...",
                    GREEN)

            # Add comments
            for c_email, c_body in issue_data.get("comments", []):
                author = user_map.get(c_email)
                if not author:
                    log("✗", f"  Comment author not found: {c_email}", RED)
                    continue

                # Check duplicate comment
                existing_comment = db.query(Comment).filter(
                    Comment.issue_id == issue_obj.id,
                    Comment.author_id == author.id,
                    Comment.body == c_body,
                ).first()

                if existing_comment:
                    continue

                if not dry_run:
                    comment = Comment(
                        issue_id=issue_obj.id,
                        author_id=author.id,
                        body=c_body,
                    )
                    db.add(comment)
                    total_comments += 1

    return total_issues, total_comments


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="IssueHub Database Seed Script")
    parser.add_argument("--reset",   action="store_true", help="Drop and recreate all tables before seeding")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to database")
    args = parser.parse_args()

    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(f"{BOLD}  IssueHub — Database Seed Script{RESET}")
    if args.dry_run:
        print(f"  {YELLOW}{BOLD}  DRY RUN MODE — nothing will be written{RESET}")
    print(f"{BOLD}{'═' * 60}{RESET}")

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if args.reset and not args.dry_run:
            confirm = input(f"\n  {YELLOW}⚠  This will DELETE all data. Type 'yes' to confirm: {RESET}")
            if confirm.strip().lower() != "yes":
                print("  Aborted.")
                return
            reset_db(db)

        user_map    = seed_users(db, dry_run=args.dry_run)
        project_map = seed_projects(db, user_map, dry_run=args.dry_run)
        total_issues, total_comments = seed_issues(db, user_map, project_map, dry_run=args.dry_run)

        if not args.dry_run:
            db.commit()

        # ── Summary ───────────────────────────────────────────
        print(f"\n{BOLD}{'═' * 60}{RESET}")
        print(f"{BOLD}  SEED COMPLETE{RESET}")
        print(f"{'═' * 60}")
        print(f"  {GREEN}Users    : {len(USERS)}{RESET}")
        print(f"  {GREEN}Projects : {len(PROJECTS)}{RESET}")
        issues_total = sum(len(v) for v in ISSUES.values())
        comments_total = sum(len(i.get('comments', [])) for v in ISSUES.values() for i in v)
        print(f"  {GREEN}Issues   : {issues_total} across {len(PROJECTS)} projects{RESET}")
        print(f"  {GREEN}Comments : {comments_total}{RESET}")
        print(f"{'═' * 60}")

        if not args.dry_run:
            print(f"\n  {BOLD}Login credentials:{RESET}")
            for u in USERS:
                print(f"  {DIM}  {u['email']:<30} password: {u['password']}{RESET}")

        print(f"\n  {GREEN}{BOLD}✓ Database seeded successfully!{RESET}")
        print(f"  {DIM}Start the server: uvicorn app.main:app --reload --port 8000{RESET}\n")

    except Exception as e:
        db.rollback()
        print(f"\n  {RED}{BOLD}✗ Seed failed: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()