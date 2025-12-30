#!/usr/bin/env python3
"""
Convert NDJSON files to Elasticsearch bulk API format with timestamp updates.

Usage: python3 convert_ndjson_to_bulk.py <input_file> <output_file> [time_offset_minutes]

Arguments:
    input_file: Path to input NDJSON file
    output_file: Path to output bulk NDJSON file
    time_offset_minutes: Optional minutes to offset timestamps from current time (default: 0)
"""

import json
import sys
from datetime import datetime, timedelta, timezone


def update_timestamp(obj, base_time):
    """Update @timestamp field to current date/hour but keep original minutes/seconds"""
    if '@timestamp' in obj:
        try:
            # Parse the original timestamp
            original_dt = datetime.fromisoformat(obj['@timestamp'].replace('Z', '+00:00'))

            # Create new timestamp with current date/hour but original minutes/seconds
            new_timestamp = base_time.replace(
                minute=original_dt.minute,
                second=original_dt.second,
                microsecond=original_dt.microsecond
            )

            obj['@timestamp'] = new_timestamp.isoformat() + 'Z'
        except (ValueError, AttributeError) as e:
            # If parsing fails, fall back to current time
            print(f"Warning: Could not parse timestamp '{obj['@timestamp']}', using current time: {e}", file=sys.stderr)
            obj['@timestamp'] = base_time.isoformat() + 'Z'
    return obj


def convert_ndjson_to_bulk(input_file, output_file, time_offset_minutes=0):
    """Convert NDJSON file to Elasticsearch bulk format with timestamp updates"""
    try:
        # Get current time as base for timestamp updates
        base_time = datetime.utcnow()

        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line_num, line in enumerate(infile, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                try:
                    # Parse JSON
                    json_obj = json.loads(line)

                    # Update timestamp to current date/hour but keep original minutes/seconds
                    json_obj = update_timestamp(json_obj, base_time)

                    # Write the create action
                    outfile.write('{ "create": {} }\n')

                    # Write the updated JSON line
                    outfile.write(json.dumps(json_obj, separators=(',', ':')) + '\n')

                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON at line {line_num}: {e}", file=sys.stderr)
                    continue

    except Exception as e:
        print(f"Error processing {input_file}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 convert_ndjson_to_bulk.py <input_file> <output_file> [time_offset_minutes]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    time_offset_minutes = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    convert_ndjson_to_bulk(input_file, output_file, time_offset_minutes)


if __name__ == "__main__":
    main()
