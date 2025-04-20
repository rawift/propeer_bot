# run_meeting.py

import sys
from meeting_manager import MeetingManager

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python run_meeting.py <meeting_link> <end_time> <mentor_name>")
        sys.exit(1)

    meeting_link = sys.argv[1]
    end_time = sys.argv[2]
    mentor_name = sys.argv[3]

    manager = MeetingManager()
    pid = manager.start_meeting(meeting_link, end_time, mentor_name)
    print(f"Meeting started with PID: {pid}")
