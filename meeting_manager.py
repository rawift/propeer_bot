import os
import time
import logging
import multiprocessing
import uuid
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# IMPORTANT: Define this function outside the class
def _run_meeting_bot_process(meeting_link, end_time, mentor_name):
    """Run as a separate process - must be defined at module level"""
    # Import inside function to avoid circular imports
    from ProPeersGoogleMeetBoat import ProPeersGoogleMeetBoat, main
    
    # Setup logging for this process
    process_id = os.getpid()
    log_file = os.path.join('logs', f'meeting_{process_id}.log')
    
    # Configure logging
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    
    logger.info(f"Starting meeting process {process_id}")
    logger.info(f"Meeting link: {meeting_link}")
    logger.info(f"End time: {end_time}")
    logger.info(f"Mentor name: {mentor_name}")
    
    try:
        # Generate unique profile ID
        unique_id = str(uuid.uuid4())[:8]
        
        # Get credentials from environment
        email = os.environ.get("email")
        password = os.environ.get("password")
        
        # Create bot
        bot = ProPeersGoogleMeetBoat(email, password, meeting_link)
        bot.setup_driver()
        
        bot.login()  
        time.sleep(1)
        bot.join_meeting()
        
        # Run main functionality
        main(bot, mentor_name)
        
        # Monitor end time
        end_time_obj = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ')
        
        while True:
            current_time = datetime.now()
            current_time_formatted = current_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time_formatted = end_time_obj.strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"Current time: {current_time_formatted}")
            logger.info(f"End time: {end_time_formatted}")
            
            if current_time_formatted >= end_time_formatted:
                logger.info("Meeting end time reached. Shutting down.")
                break
            
            time.sleep(60)  # Check every minute
            
    except Exception as e:
        logger.error(f"Error in meeting process: {e}", exc_info=True)
    finally:
        logger.info("Closing meeting session")
        if 'bot' in locals() and hasattr(bot, 'driver'):
            bot.close_driver()

class MeetingManager:
    def __init__(self):
        self.processes = []


    def start_meeting(self, meeting_link, end_time, mentor_name):
        """Start a new meeting in a separate process"""
        # Create process using standalone function
        print("in meet manager")
        process = multiprocessing.Process(
            target=_run_meeting_bot_process,
            args=(meeting_link, end_time, mentor_name)
        )
        process.start()
        self.processes.append(process)
        return process.pid
        
    def list_active_meetings(self):
        """List all active meeting processes"""
        return [p.pid for p in self.processes if p.is_alive()]
        
    def stop_meeting(self, process_id):
        """Stop a meeting by process ID"""
        for i, process in enumerate(self.processes):
            if process.pid == process_id and process.is_alive():
                process.terminate()
                process.join(timeout=5)
                return True
        return False