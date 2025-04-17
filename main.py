import os
import re
from collections import defaultdict


log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
route_pattern = re.compile(r'(/api/v1/[^\s]+|/admin/[^\s]+)', re.IGNORECASE)
log_level_pattern = re.compile(r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b', re.IGNORECASE)
db_query_pattern = re.compile(r'\bDEBUG\b.*SELECT.*FROM', re.IGNORECASE)


def parse_logs(log_file):
    route_log_counts = defaultdict(lambda: defaultdict(int))
    total_logs = 0
    db_queries = 0

    with open(log_file, 'r') as file:
        for line in file:
            total_logs += 1

            route_match = route_pattern.search(line)

            level_match = log_level_pattern.search(line)

            if db_query_pattern.search(line):
                db_queries += 1
                level = 'DEBUG'
                route = 'No route'

            elif level_match:
                level = level_match.group(0).upper()

                if route_match:
                    route = route_match.group(0)
                else:
                    route = 'No route'

            route_log_counts[route][level] += 1

    return route_log_counts, total_logs, db_queries


def write_results(route_log_counts, total_logs_per_file, db_queries, output_file):
    with open(output_file, 'w') as file:
        header = ['HANDLER', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        file.write("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(*header))
        print("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*header))

        for route, counts in route_log_counts.items():
            row = [route]
            for level in log_levels:
                row.append(str(counts.get(level, 0)))
            file.write("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(*row))
            print("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*row))

        total_by_level = defaultdict(int)
        for counts in route_log_counts.values():
            for level in log_levels:
                total_by_level[level] += counts.get(level, 0)

        total_row = ['Total requests:']
        for level in log_levels:
            total_row.append(str(total_by_level[level]))
        file.write("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(*total_row))
        print("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*total_row))

        total_logs = sum(total_logs_per_file)
        file.write(f"\nTotal logs processed across all files: {total_logs}\n")
        print(f"\nTotal logs processed across all files: {total_logs}")

        file.write(f"\nTotal DEBUG logs with database queries (No route): {db_queries}\n")
        print(
            f"\nTotal DEBUG logs with database queries (No route): {db_queries}")


def process_all_logs(log_directory, output_file):
    route_log_counts = defaultdict(lambda: defaultdict(int))
    total_logs_per_file = []
    db_queries = 0

    for filename in os.listdir(log_directory):
        if filename.endswith(".log"):
            log_file_path = os.path.join(log_directory, filename)
            print(f"Processing file: {filename}")
            file_counts, total_logs, file_db_queries = parse_logs(log_file_path)
            total_logs_per_file.append(total_logs)
            db_queries += file_db_queries

            for route, counts in file_counts.items():
                for level, count in counts.items():
                    route_log_counts[route][level] += count

    write_results(route_log_counts, total_logs_per_file, db_queries, output_file)


log_directory = 'logs'
output_file = 'sum_logs.txt'

process_all_logs(log_directory, output_file)
