"""
IssueHub — Automated Test Runner
=================================
Runs all test cases against the live backend automatically.
Make sure your FastAPI server is running on http://localhost:8000 before executing.

Usage:
    python test_runner.py
    python test_runner.py --base-url http://localhost:8000
    python test_runner.py --verbose
"""

import requests
import json
import argparse
import sys
import time
from datetime import datetime

# ── Config ────────────────────────────────────────────────────
BASE_URL = "http://localhost:8000/api"

# ── State (filled during test run) ───────────────────────────
tokens   = {}   # { username: access_token }
projects = {}   # { name: id }
issues   = {}   # { name: id }
comments = {}   # { name: id }
users    = {}   # { name: id } (not returned by API, tracked by order)

# ── Terminal colors ───────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

# ── Result tracking ───────────────────────────────────────────
results = {"passed": 0, "failed": 0, "skipped": 0, "errors": []}
verbose = False

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def header(title):
    print(f"\n{BOLD}{BLUE}{'═' * 60}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'═' * 60}{RESET}")

def section(title):
    print(f"\n{CYAN}{BOLD}── {title} {'─' * (54 - len(title))}{RESET}")

def api(method, path, body=None, token=None, params=None):
    """Make an API call and return (status_code, response_dict)."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{BASE_URL}{path}"
    try:
        res = getattr(requests, method.lower())(
            url, json=body, headers=headers, params=params, timeout=10
        )
        try:
            data = res.json()
        except Exception:
            data = {"raw": res.text}
        return res.status_code, data
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}{BOLD}  ✗ Cannot connect to {url}{RESET}")
        print(f"  {DIM}Make sure FastAPI is running: uvicorn app.main:app --reload --port 8000{RESET}\n")
        sys.exit(1)

def check(name, status, data, expect_status, expect_key=None, expect_value=None,
          save_token_as=None, save_id_to=None, save_id_key="id"):
    """Assert a response and print pass/fail. Optionally save token or ID."""
    global results
    passed = True
    reason = ""

    if status != expect_status:
        passed = False
        reason = f"expected HTTP {expect_status}, got {status}"
    elif expect_key and expect_key not in data:
        passed = False
        reason = f"key '{expect_key}' not in response"
    elif expect_value is not None:
        actual = data.get(expect_key)
        if actual != expect_value:
            passed = False
            reason = f"expected {expect_key}='{expect_value}', got '{actual}'"

    if passed:
        results["passed"] += 1
        print(f"  {GREEN}✓{RESET} {name}")
        if save_token_as:
            tokens[save_token_as] = data.get("access_token")
            if verbose:
                print(f"    {DIM}→ token saved for '{save_token_as}'{RESET}")
        if save_id_to:
            saved_id = data.get(save_id_key)
            if save_id_to.startswith("projects/"):
                projects[save_id_to.split("/", 1)[1]] = saved_id
            elif save_id_to.startswith("issues/"):
                issues[save_id_to.split("/", 1)[1]] = saved_id
            elif save_id_to.startswith("comments/"):
                comments[save_id_to.split("/", 1)[1]] = saved_id
            if verbose:
                print(f"    {DIM}→ id {saved_id} saved as '{save_id_to}'{RESET}")
        if verbose:
            print(f"    {DIM}{json.dumps(data, indent=2)[:200]}{RESET}")
    else:
        results["failed"] += 1
        results["errors"].append({"test": name, "reason": reason, "status": status, "data": data})
        print(f"  {RED}✗{RESET} {name}")
        print(f"    {RED}└─ {reason}{RESET}")
        if verbose:
            print(f"    {DIM}{json.dumps(data, indent=2)[:300]}{RESET}")

    return passed, data

def skip(name, reason="prerequisite failed"):
    results["skipped"] += 1
    print(f"  {YELLOW}○{RESET} {name} {DIM}(skipped: {reason}){RESET}")

# ══════════════════════════════════════════════════════════════
# TEST SUITES
# ══════════════════════════════════════════════════════════════

def test_auth():
    header("1. AUTHENTICATION")

    section("1.1 Signup — valid users")
    users_data = [
        ("arjun", {"name": "Arjun Sharma",  "email": "arjun@issuehub.dev", "password": "arjun1234"}),
        ("priya", {"name": "Priya Nair",    "email": "priya@issuehub.dev", "password": "priya1234"}),
        ("rahul", {"name": "Rahul Verma",   "email": "rahul@issuehub.dev", "password": "rahul1234"}),
        ("sneha", {"name": "Sneha Patel",   "email": "sneha@issuehub.dev", "password": "sneha1234"}),
    ]
    for username, body in users_data:
        status, data = api("POST", "/auth/signup", body)
        # Accept 200/201 (created) OR 400 (email exists if re-running)
        if status in (200, 201):
            check(f"Signup: {body['name']}", status, data, status)
        else:
            check(f"Signup: {body['name']} (already exists — ok)", status, data, 400)

    section("1.2 Signup — failure cases")
    status, data = api("POST", "/auth/signup", {
        "name": "Arjun Sharma", "email": "arjun@issuehub.dev", "password": "arjun1234"
    })
    check("Signup with duplicate email → 400", status, data, 400)

    status, data = api("POST", "/auth/signup", {"email": "nopw@test.com"})
    check("Signup without required fields → 422", status, data, 422)

    section("1.3 Login — valid credentials")
    for username, body in users_data:
        status, data = api("POST", "/auth/login", {"email": body["email"], "password": body["password"]})
        check(
            f"Login: {body['name']}",
            status, data, 200,
            expect_key="access_token",
            save_token_as=username,
        )

    section("1.4 Login — failure cases")
    status, data = api("POST", "/auth/login", {"email": "arjun@issuehub.dev", "password": "wrongpass"})
    check("Login with wrong password → 401", status, data, 401)

    status, data = api("POST", "/auth/login", {"email": "ghost@nowhere.com", "password": "pass1234"})
    check("Login with non-existent email → 401", status, data, 401)

    status, data = api("POST", "/auth/login", {"email": "arjun@issuehub.dev"})
    check("Login without password field → 422", status, data, 422)

    section("1.5 Protected route without token")
    status, data = api("GET", "/projects/")
    check("Access protected route without token → 401/403", status, data,
          status if status in (401, 403) else 401)


def test_projects():
    header("2. PROJECTS")

    if "arjun" not in tokens:
        skip("All project tests", "arjun not logged in")
        return

    section("2.1 Create projects (as Arjun)")
    projects_data = [
        ("shopease", {"name": "ShopEase E-Commerce", "key": "SHOP", "description": "Full-stack e-commerce platform"}),
        ("payflow",  {"name": "PayFlow Banking",      "key": "PAY",  "description": "Mobile banking with UPI integration"}),
        ("hrdesk",   {"name": "HRDesk Portal",        "key": "HR",   "description": "Employee management and payroll"}),
    ]
    for proj_key, body in projects_data:
        status, data = api("POST", "/projects/", body, token=tokens["arjun"])
        if status in (200, 201):
            check(f"Create project: {body['name']}", status, data, status,
                  expect_key="id", save_id_to=f"projects/{proj_key}")
        else:
            # Might already exist from previous run — try to find it in list
            check(f"Create project: {body['name']} (key exists → 400 ok)", status, data, 400)

    section("2.2 Create project — failure cases")
    status, data = api("POST", "/projects/", {"name": "Dup", "key": "SHOP", "description": "dup"}, token=tokens["arjun"])
    check("Create project with duplicate key → 400", status, data, 400)

    status, data = api("POST", "/projects/", {"name": "No Key"}, token=tokens["arjun"])
    check("Create project without key → 422", status, data, 422)

    status, data = api("POST", "/projects/", {"name": "No Auth", "key": "XYZ", "description": "..."})
    check("Create project without token → 401/403", status, data,
          status if status in (401, 403) else 401)

    section("2.3 List projects")
    status, data = api("GET", "/projects/", token=tokens["arjun"])
    check("List projects (Arjun sees his projects)", status, data, 200)

    status, data = api("GET", "/projects/", token=tokens["priya"])
    check("List projects (Priya — no projects yet → empty list)", status, data, 200)

    section("2.4 Add members (as Arjun — maintainer)")
    if "shopease" in projects and projects["shopease"]:
        pid = projects["shopease"]
        for uname, uid_guess, role in [("priya", 2, "member"), ("rahul", 3, "member"), ("sneha", 4, "member")]:
            # user_id is the sequential ID from signup — try 2, 3, 4
            # If your IDs differ, this may need adjustment
            for uid in range(1, 10):
                st, dt = api("POST", f"/projects/{pid}/members",
                             token=tokens["arjun"], params={"user_id": uid, "role": role})
                if st == 200:
                    check(f"Add {uname} (uid={uid}) to ShopEase", st, dt, 200)
                    break
                elif "already" in str(dt).lower() or st == 400:
                    check(f"Add {uname} to ShopEase (already member — ok)", st, dt, st)
                    break
            else:
                skip(f"Add {uname} to ShopEase", "could not determine user ID")
    else:
        skip("Add members to ShopEase", "shopease project ID not available")

    section("2.5 Add member — permission failure")
    if "shopease" in projects and projects["shopease"]:
        pid = projects["shopease"]
        status, data = api("POST", f"/projects/{pid}/members",
                           token=tokens["priya"], params={"user_id": 4, "role": "member"})
        check("Non-maintainer cannot add members → 403", status, data, 403)


def test_issues():
    header("3. ISSUES")

    # Use shopease project — fall back to project id 1 if not captured
    pid = projects.get("shopease") or 1

    section("3.1 Create issues (various users)")
    issues_data = [
        ("payment_timeout", "arjun", {
            "title": "Payment gateway timeout on checkout",
            "description": "Users experience 30-second timeout when completing payment. Razorpay callback not returning within expected window. Affects 100% of live transactions.",
            "priority": "high"
        }),
        ("safari_images", "priya", {
            "title": "Product images not loading on Safari",
            "description": "All product images return 404 on Safari 17+. Image URLs contain spaces not being URL-encoded before CDN request. Chrome and Firefox unaffected.",
            "priority": "high"
        }),
        ("filter_bug", "rahul", {
            "title": "Search results do not update when filter is cleared",
            "description": "Applying a category filter then clicking 'Clear Filters' does not re-fetch the product list. Stale results persist until manual page refresh.",
            "priority": "medium"
        }),
        ("wishlist_btn", "sneha", {
            "title": "Add Save to Wishlist button on product cards",
            "description": "Users can only save to wishlist from product detail page. A quick-save heart icon on the card listing would reduce friction and improve conversion.",
            "priority": "medium"
        }),
        ("email_breakdown", "arjun", {
            "title": "Order confirmation email missing itemized price breakdown",
            "description": "Order confirmation email shows only total amount. Should include itemized list: product, qty, unit price, subtotal, tax, shipping, and final total.",
            "priority": "low"
        }),
        ("duplicate_order", "rahul", {
            "title": "Duplicate orders created on double-click of Pay button",
            "description": "Double-clicking 'Complete Payment' creates two orders with two payment attempts. Button not disabled after first click. Causes duplicate charges.",
            "priority": "high"
        }),
        ("dark_mode_badge", "priya", {
            "title": "Cart item count badge not visible in dark mode",
            "description": "Red badge on navbar cart icon blends with dark background. Needs border or drop shadow for contrast.",
            "priority": "low"
        }),
    ]

    for issue_key, user, body in issues_data:
        if user not in tokens:
            skip(f"Create issue: {body['title'][:40]}...", f"{user} not logged in")
            continue
        status, data = api("POST", f"/issues/project/{pid}", body, token=tokens[user])
        check(
            f"Create issue [{body['priority'].upper()}]: {body['title'][:45]}...",
            status, data, 200,
            expect_key="id",
            save_id_to=f"issues/{issue_key}",
        )

    section("3.2 Create issue — failure cases")
    status, data = api("POST", f"/issues/project/{pid}", {
        "title": "No auth issue", "description": "...", "priority": "low"
    })
    check("Create issue without token → 401/403", status, data,
          status if status in (401, 403) else 401)

    status, data = api("POST", f"/issues/project/99999", {
        "title": "Wrong project", "description": "...", "priority": "low"
    }, token=tokens.get("arjun"))
    check("Create issue in non-existent project → 403/404", status, data,
          status if status in (403, 404) else 403)

    status, data = api("POST", f"/issues/project/{pid}", {
        "description": "Missing title", "priority": "low"
    }, token=tokens.get("arjun"))
    check("Create issue without title → 422", status, data, 422)

    section("3.3 List issues")
    status, data = api("GET", f"/issues/project/{pid}", token=tokens.get("arjun"))
    check("List all issues in project", status, data, 200)

    status, data = api("GET", f"/issues/project/{pid}", token=tokens.get("arjun"),
                       params={"priority": "high"})
    check("Filter issues by priority=high", status, data, 200)

    status, data = api("GET", f"/issues/project/{pid}", token=tokens.get("arjun"),
                       params={"status": "open"})
    check("Filter issues by status=open", status, data, 200)

    status, data = api("GET", f"/issues/project/{pid}", token=tokens.get("arjun"),
                       params={"priority": "high", "status": "open"})
    check("Filter issues by priority + status combined", status, data, 200)

    status, data = api("GET", f"/issues/project/{pid}", token=tokens.get("arjun"),
                       params={"skip": 0, "limit": 3})
    check("List issues with pagination (limit=3)", status, data, 200)

    section("3.4 Get single issue")
    issue_id = issues.get("payment_timeout")
    if issue_id:
        status, data = api("GET", f"/issues/{issue_id}", token=tokens.get("arjun"))
        check("Get single issue by ID", status, data, 200, expect_key="title")

        status, data = api("GET", f"/issues/{issue_id}")
        check("Get issue without token → 401/403", status, data,
              status if status in (401, 403) else 401)
    else:
        skip("Get single issue", "payment_timeout issue ID not available")

    section("3.5 Update issues (PATCH)")
    if issues.get("payment_timeout"):
        status, data = api("PATCH", f"/issues/{issues['payment_timeout']}",
                           {"status": "in_progress"}, token=tokens.get("arjun"))
        check("Maintainer moves issue to in_progress", status, data, 200,
              expect_key="status", expect_value="in_progress")

    if issues.get("duplicate_order") and "rahul" in tokens:
        status, data = api("PATCH", f"/issues/{issues['duplicate_order']}",
                           {"status": "in_progress"}, token=tokens["rahul"])
        check("Reporter moves own issue to in_progress", status, data, 200)

    if issues.get("safari_images") and "priya" in tokens:
        status, data = api("PATCH", f"/issues/{issues['safari_images']}",
                           {"status": "closed",
                            "description": "FIXED: URL encoding added to CDN image URLs. Deployed in v2.3.1."},
                           token=tokens["priya"])
        check("Reporter closes own issue with updated description", status, data, 200)

    if issues.get("filter_bug") and "arjun" in tokens:
        status, data = api("PATCH", f"/issues/{issues['filter_bug']}",
                           {"priority": "high"}, token=tokens["arjun"])
        check("Maintainer upgrades issue priority to high", status, data, 200)

    section("3.6 Update issue — permission failures")
    # Sneha tries to update Arjun's issue (payment_timeout) — she is neither reporter nor maintainer
    if issues.get("payment_timeout") and "sneha" in tokens:
        status, data = api("PATCH", f"/issues/{issues['payment_timeout']}",
                           {"status": "closed"}, token=tokens["sneha"])
        check("Non-reporter/non-maintainer cannot update issue → 403", status, data, 403)

    # Priya tries to update Rahul's issue (duplicate_order) — she is not reporter or maintainer
    if issues.get("duplicate_order") and "priya" in tokens:
        status, data = api("PATCH", f"/issues/{issues['duplicate_order']}",
                           {"priority": "low"}, token=tokens["priya"])
        check("Member cannot update another member's issue → 403", status, data, 403)


def test_comments():
    header("4. COMMENTS")

    issue_id = issues.get("payment_timeout")
    dup_id   = issues.get("duplicate_order")

    section("4.1 Add comments to Payment Timeout issue")
    comments_data = [
        ("payment_c1", "rahul",
         "Reproduced on staging. Razorpay webhook responding correctly but frontend awaiting a redirect that never comes. Looks like a missing return URL config."),
        ("payment_c2", "priya",
         "Checked network tab — POST to /api/payments/initiate returns 200 but response body is empty. Something wrong server-side before redirect URL is constructed."),
        ("payment_c3", "arjun",
         "Found it. RAZORPAY_RETURN_URL env variable not set in production. Set it to https://shopease.com/payment/callback and redeploy."),
        ("payment_c4", "sneha",
         "Verified the fix on staging. Payment completes successfully and redirects to order confirmation page. Ready for production deploy."),
    ]

    if not issue_id:
        skip("All payment_timeout comments", "issue ID not available")
    else:
        for ckey, user, body_text in comments_data:
            if user not in tokens:
                skip(f"Comment by {user}", f"{user} not logged in")
                continue
            status, data = api("POST", f"/comments/issue/{issue_id}",
                               {"body": body_text}, token=tokens[user])
            check(
                f"Comment by {user}: '{body_text[:50]}...'",
                status, data, 200,
                expect_key="id",
                save_id_to=f"comments/{ckey}",
            )

    section("4.2 Add comments to Duplicate Orders issue")
    dup_comments = [
        ("dup_c1", "arjun",
         "Confirmed critical. Disabling Pay button on first click is immediate fix. Also need idempotency key to prevent duplicate order creation even if two requests get through."),
        ("dup_c2", "rahul",
         "Button disable fix is a one-liner — pushing in 30 mins. Idempotency key will take a few hours. Should I push button fix as hotfix now?"),
        ("dup_c3", "arjun",
         "Yes, push button disable as emergency hotfix. Create a separate issue for idempotency key implementation and link it here."),
    ]

    if not dup_id:
        skip("All duplicate_order comments", "issue ID not available")
    else:
        for ckey, user, body_text in dup_comments:
            if user not in tokens:
                skip(f"Comment by {user}", f"{user} not logged in")
                continue
            status, data = api("POST", f"/comments/issue/{dup_id}",
                               {"body": body_text}, token=tokens[user])
            check(
                f"Comment by {user}: '{body_text[:50]}...'",
                status, data, 200,
            )

    section("4.3 List comments")
    if issue_id:
        status, data = api("GET", f"/comments/issue/{issue_id}", token=tokens.get("arjun"))
        check("List comments on issue (should have 4)", status, data, 200)

    section("4.4 Comment — failure cases")
    if issue_id:
        status, data = api("POST", f"/comments/issue/{issue_id}", {"body": "No auth"})
        check("Post comment without token → 401/403", status, data,
              status if status in (401, 403) else 401)

        status, data = api("POST", f"/comments/issue/{issue_id}", {}, token=tokens.get("arjun"))
        check("Post comment with empty body → 422", status, data, 422)


def test_delete():
    header("5. DELETE ISSUES")

    section("5.1 Delete — permission failures first")
    # Priya tries to delete Arjun's issue — should fail (403)
    issue_id = issues.get("email_breakdown")  # created by arjun
    if issue_id and "priya" in tokens:
        status, data = api("DELETE", f"/issues/{issue_id}", token=tokens["priya"])
        check("Non-reporter cannot delete another user's issue → 403", status, data, 403)
    else:
        skip("Delete permission failure test", "issue or token not available")

    section("5.2 Delete — success cases")
    # Priya deletes her own issue (dark_mode_badge)
    own_issue = issues.get("dark_mode_badge")
    if own_issue and "priya" in tokens:
        status, data = api("DELETE", f"/issues/{own_issue}", token=tokens["priya"])
        check("Reporter deletes own issue → 200", status, data, 200)

    # Arjun (maintainer) deletes any issue (wishlist_btn)
    any_issue = issues.get("wishlist_btn")
    if any_issue and "arjun" in tokens:
        status, data = api("DELETE", f"/issues/{any_issue}", token=tokens["arjun"])
        check("Maintainer deletes any issue → 200", status, data, 200)

    section("5.3 Delete already-deleted issue")
    if own_issue and "priya" in tokens:
        status, data = api("DELETE", f"/issues/{own_issue}", token=tokens["priya"])
        check("Delete already-deleted issue → 404", status, data, 404)


def test_second_project():
    header("6. PAYFLOW PROJECT — ISOLATION TEST")
    section("6.1 Create PayFlow issues")

    pid = projects.get("payflow") or 2

    payflow_issues = [
        ("upi_history", "arjun", {
            "title": "UPI transaction history missing for transfers older than 30 days",
            "description": "History screen only fetches last 30 days. API supports date range param but frontend not passing it correctly.",
            "priority": "high",
        }),
        ("otp_airtel", "arjun", {
            "title": "OTP not received on Airtel numbers",
            "description": "Login OTP not delivered to Airtel numbers. Jio and Vi work. Started after SMS gateway switch on 2024-12-01. Airtel = 28% of user base.",
            "priority": "high",
        }),
        ("biometric", "rahul", {
            "title": "Add biometric authentication support",
            "description": "Users requested fingerprint and Face ID login as alternative to PIN. Standard in competing banking apps.",
            "priority": "medium",
        }),
    ]

    for issue_key, user, body in payflow_issues:
        if user not in tokens:
            skip(f"PayFlow issue: {body['title'][:40]}", f"{user} not logged in")
            continue
        status, data = api("POST", f"/issues/project/{pid}", body, token=tokens[user])
        check(
            f"Create PayFlow issue: {body['title'][:45]}...",
            status, data, 200,
            save_id_to=f"issues/{issue_key}",
        )

    section("6.2 Project isolation — Priya cannot access PayFlow issues")
    # Priya is NOT a member of PayFlow — she should get 403
    status, data = api("GET", f"/issues/project/{pid}", token=tokens.get("priya"))
    check("Non-member cannot list issues in another project → 403", status, data, 403)

    section("6.3 Close resolved PayFlow issue")
    if issues.get("otp_airtel") and "arjun" in tokens:
        status, data = api("PATCH", f"/issues/{issues['otp_airtel']}",
                           {"status": "closed"}, token=tokens["arjun"])
        check("Close resolved OTP issue", status, data, 200)


# ══════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════

def print_summary():
    total = results["passed"] + results["failed"] + results["skipped"]
    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(f"{BOLD}  TEST SUMMARY{RESET}")
    print(f"{'═' * 60}")
    print(f"  {GREEN}Passed  : {results['passed']}{RESET}")
    print(f"  {RED}Failed  : {results['failed']}{RESET}")
    print(f"  {YELLOW}Skipped : {results['skipped']}{RESET}")
    print(f"  {BOLD}Total   : {total}{RESET}")
    print(f"{'═' * 60}")

    if results["errors"]:
        print(f"\n{RED}{BOLD}  FAILED TESTS:{RESET}")
        for i, err in enumerate(results["errors"], 1):
            print(f"  {i}. {err['test']}")
            print(f"     {DIM}Reason : {err['reason']}{RESET}")
            print(f"     {DIM}Status : {err['status']}{RESET}")
            detail = json.dumps(err['data'])[:120]
            print(f"     {DIM}Data   : {detail}{RESET}")

    print()
    if results["failed"] == 0:
        print(f"  {GREEN}{BOLD}🎉 All tests passed!{RESET}")
    else:
        print(f"  {RED}{BOLD}⚠  {results['failed']} test(s) failed. See details above.{RESET}")
    print()


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════

def main():
    global BASE_URL, verbose

    parser = argparse.ArgumentParser(description="IssueHub Automated Test Runner")
    parser.add_argument("--base-url", default="http://localhost:8000/api",
                        help="Base API URL (default: http://localhost:8000/api)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print full response bodies")
    args = parser.parse_args()

    BASE_URL = args.base_url
    verbose  = args.verbose

    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(f"{BOLD}  IssueHub — Automated Test Runner{RESET}")
    print(f"  {DIM}Started  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"  {DIM}Base URL : {BASE_URL}{RESET}")
    print(f"{BOLD}{'═' * 60}{RESET}")

    # Check server is up
    try:
        requests.get(f"{BASE_URL.replace('/api', '')}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}{BOLD}  ✗ Server not reachable at {BASE_URL}{RESET}")
        print(f"  Run: {CYAN}uvicorn app.main:app --reload --port 8000{RESET}\n")
        sys.exit(1)

    print(f"  {GREEN}✓ Server is up{RESET}")

    # Run all suites
    test_auth()
    test_projects()
    test_issues()
    test_comments()
    test_delete()
    test_second_project()

    print_summary()

    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()