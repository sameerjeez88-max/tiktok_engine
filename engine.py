import os
import random
import time
import json
import cv2
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_DIR = os.path.join(BASE_DIR, 'accounts')
SESSIONS_DIR = os.path.join(BASE_DIR, 'sessions')
os.makedirs(SESSIONS_DIR, exist_ok=True)

TRADING_TITLES = [
    "AI Trading Bot hitting massive profits! 🚀",
    "Passive income with automated crypto & forex trading 📈",
    "Smart AI signals for XAUUSD market analysis 💡",
    "How our automated algorithm predicts market trends 🤖",
    "Consistent daily gains using Winvest smart engine 💰",
    "Next-level algorithmic trading in action 🔥"
]

TRENDING_HASHTAG_POOLS = [
    ["#fyp", "#foryou", "#viral", "#trending", "#trading", "#crypto", "#forex", "#ai"],
    ["#daytrading", "#investing", "#passiveincome", "#wealth", "#finance", "#binance", "#trader", "#algorithm"],
    ["#makemoneyonline", "#business", "#success", "#money", "#xauusd", "#signals", "#automatedtrading", "#foryoupage"]
]

def analyze_video_and_generate_metadata(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    mid_frame = total_frames // 2 if total_frames > 0 else 0
    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
    ret, frame = cap.read()
    cap.release()
    
    thumbnail_path = video_path.rsplit('.', 1)[0] + '_cover.jpg'
    if ret:
        cv2.imwrite(thumbnail_path, frame)
        try:
            img = Image.open(thumbnail_path)
            draw = ImageDraw.Draw(img)
            draw.text((20, 20), "AI TRADING", fill=(0, 255, 255))
            img.save(thumbnail_path)
        except Exception as e:
            print(f"Thumbnail text drawing error: {e}")
    
    selected_title = random.choice(TRADING_TITLES)
    
    chosen_tags = []
    for pool in TRENDING_HASHTAG_POOLS:
        chosen_tags.extend(random.sample(pool, min(3, len(pool))))
    
    base_hashtags = " ".join(list(set(chosen_tags)))
    caption = f"{selected_title} \n\n👉 Link in Bio to Join Now: https://winvest-aad06.web.app/ \n\n{base_hashtags}"
    
    return caption, thumbnail_path

def upload_to_tiktok_and_schedule(account_name, video_path, caption, hours_ahead):
    session_dir = os.path.join(SESSIONS_DIR, account_name)
    os.makedirs(session_dir, exist_ok=True)
    
    print(f"[{account_name}] Starting schedule upload for: {os.path.basename(video_path)} (Scheduled +{hours_ahead} hours)")
    is_headless = False  
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=is_headless,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            viewport=None
        )
        page = browser.new_page()
        
        try:
            print(f"[{account_name}] Opening TikTok Creator Center upload page...")
            page.goto("https://www.tiktok.com/creator-center/upload", timeout=90000)
            time.sleep(6)
            
            if "login" in page.url or "signin" in page.url:
                print(f"\n[!] ALERT [{account_name}]: Please log in to your TikTok account manually.")
                page.wait_for_url("**/creator-center/upload**", timeout=120000)
                time.sleep(5)
            
            print(f"[{account_name}] Uploading video file...")
            file_input = page.locator('input[type="file"]').first
            file_input.set_input_files(video_path)
            
            print(f"[{account_name}] Waiting for video processing and pop-ups...")
            time.sleep(10) 
            
            try:
                got_it_btn = page.locator('button:has-text("Got it")').last
                if got_it_btn.is_visible(timeout=5000):
                    got_it_btn.click()
                    print(f"[{account_name}] 'Got it' popup dismissed.")
                    time.sleep(2)
            except:
                pass

            try:
                turn_on_btn = page.locator('button:has-text("Turn on")').last
                if turn_on_btn.is_visible(timeout=3000):
                    turn_on_btn.click()
                    print(f"[{account_name}] 'Turn on' popup handled.")
                    time.sleep(2)
            except:
                pass
            
            try:
                caption_box = page.locator('div[contenteditable="true"]').first
                caption_box.click()
                time.sleep(1)
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                time.sleep(1)
                page.keyboard.insert_text(caption)
                print(f"[{account_name}] Smart trading caption filled successfully.")
            except Exception as ex:
                print(f"[{account_name}] Warning caption fill error: {ex}")
            
            time.sleep(3)
            
            try:
                schedule_radio = page.locator('label:has-text("Schedule")').or_(page.locator('text=Schedule')).first
                if schedule_radio.is_visible(timeout=5000):
                    schedule_radio.click()
                    print(f"[{account_name}] Schedule option selected.")
                    time.sleep(2)
                
                target_time = datetime.now() + timedelta(hours=hours_ahead)
                target_date_str = target_time.strftime("%Y-%m-%d")
                target_time_str = target_time.strftime("%H:%M")
                
                print(f"[{account_name}] Setting schedule time to: {target_time.strftime('%Y-%m-%d %H:%M')}")
                
                # Set Date
                date_input = page.locator('input[placeholder*="Date"]').or_(page.locator('input[type="date"]')).first
                if date_input.is_visible(timeout=3000):
                    date_input.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.keyboard.insert_text(target_date_str)
                    page.keyboard.press("Enter")
                    time.sleep(1)

                # Set Time (Hours & Minutes)
                time_input = page.locator('input[placeholder*="Time"]').or_(page.locator('input[type="time"]')).first
                if time_input.is_visible(timeout=3000):
                    time_input.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.keyboard.insert_text(target_time_str)
                    page.keyboard.press("Enter")
                    time.sleep(1)

            except Exception as e:
                print(f"[{account_name}] Schedule configuration note: {e}")

            time.sleep(2)
            
            post_button = page.locator('button:has-text("Schedule")').last
            if post_button.is_visible():
                post_button.click()
                print(f"[{account_name}] Schedule button clicked successfully!")
                time.sleep(4)
                
                try:
                    continue_post_btn = page.locator('button:has-text("Post now")').or_(page.locator('button:has-text("Confirm")')).or_(page.locator('button:has-text("Schedule")')).last
                    if continue_post_btn.is_visible(timeout=4000):
                        continue_post_btn.click()
                        print(f"[{account_name}] 'Continue to post' warning confirmation handled!")
                except Exception as ex:
                    print(f"[{account_name}] No confirmation modal needed or handled: {ex}")

                time.sleep(6)
            
            browser.close()
            return True
            
        except Exception as e:
            print(f"[{account_name}] Upload/Schedule Failed: {e}")
            try:
                browser.close()
            except:
                pass
            return False

def process_queue():
    if not os.path.exists(ACCOUNTS_DIR):
        print("Accounts directory not found.")
        return

    while True:
        accounts = [d for d in os.listdir(ACCOUNTS_DIR) if os.path.isdir(os.path.join(ACCOUNTS_DIR, d))]
        if not accounts:
            print("No accounts found. Waiting 30 seconds...")
            time.sleep(30)
            continue

        for account in accounts:
            acc_path = os.path.join(ACCOUNTS_DIR, account)
            raw_dir = os.path.join(acc_path, 'raw_videos')
            uploaded_dir = os.path.join(acc_path, 'uploaded')
            config_file = os.path.join(acc_path, 'config.json')
            
            os.makedirs(raw_dir, exist_ok=True)
            os.makedirs(uploaded_dir, exist_ok=True)
            
            config = {"min_hours": 4, "max_hours": 8}
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config.update(json.load(f))
                except:
                    pass
            
            videos = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.mp4', '.mov', '.webm'))]
            if not videos:
                continue 
            
            cumulative_hours = 4 
            
            for index, target_video_name in enumerate(videos):
                target_video_path = os.path.join(raw_dir, target_video_name)
                print(f"\n--- Scheduling Account: {account} | Video: {target_video_name} ---")
                
                caption, cover_path = analyze_video_and_generate_metadata(target_video_path)
                
                hours_ahead = cumulative_hours + (index * 4)
                success = upload_to_tiktok_and_schedule(account, target_video_path, caption, hours_ahead)
                
                if success:
                    dest_path = os.path.join(uploaded_dir, target_video_name)
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    os.rename(target_video_path, dest_path)
                    
                    if os.path.exists(cover_path):
                        try:
                            os.remove(cover_path)
                        except:
                            pass
                    print(f"[{account}] Video successfully scheduled on TikTok!")
                else:
                    print(f"[{account}] Failed to schedule this video. Skipping to next.")
                
                time.sleep(10)
            
            print(f"\n[{account}] All raw videos processed and scheduled! Sleeping for 1 hour before checking new videos...")
            time.sleep(3600)
        
        time.sleep(60)

if __name__ == "__main__":
    print("TikTok Auto-Pilot Scheduler Worker Started...")
    process_queue()