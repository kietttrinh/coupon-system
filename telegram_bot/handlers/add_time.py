"""
Implementation of the /add_time Telegram bot command.

This module handles adding new time schedules to existing coupons:
- Parses command arguments for coupon ID and schedule timing
- Validates that the coupon exists and user has admin privileges
- Retrieves existing schedules for the coupon from database
- Applies overlap processing algorithm to check for conflicts
- If no overlap, inserts the new schedule into the database
- Sends success or detailed error message back to the admin user
- Provides specific feedback about which existing schedule conflicts if any

The command format typically follows:
/add_time <coupon_id> <start_timestamp> <end_timestamp>

Timestamps should be in a format parsable by the system (ISO format, Unix time, etc.)
The overlap processing algorithm from algorithms/merge_intervals is used
to validate that the new schedule doesn't conflict with existing ones.
"""