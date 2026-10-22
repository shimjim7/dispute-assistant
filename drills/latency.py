from collections import defaultdict
import math

def get_latency_stats(data):
    users = defaultdict(list)

    for item in data:
        users[item["user"]].append(item["latency_ms"])

    result = {}

    for user, latencies in users.items():
        latencies.sort()

        avg = sum(latencies) / len(latencies)
        p95 = latencies[math.ceil(0.95 * len(latencies)) - 1]

        result[user] = {
            "average": avg,
            "p95": p95
        }

    return result