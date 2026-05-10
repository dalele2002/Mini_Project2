from mrjob.job import MRJob
import csv, sys, os, time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

INPUT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "download_data", "Comp3041J MiniProject 2 Dataset.csv"))


class MicroserviceLogAnalysis(MRJob):

    def mapper(self, _, line):
        try:
            row = next(csv.reader([line]))
            if row[0] == "timestamp":
                return
            service, endpoint, status, rt = row[3], row[4], int(row[6]), float(row[7])

            # Example: 2026-04-10T09:15:22Z,R00023,U104,auth-service,/login,POST,200,142,eu-west,
            # Emitted key-value: ("REQ|auth-service", 1)
            yield f"REQ|{service}", 1

            if status >= 500:
                # Example: ...,payment-service,...,500,1340,eu-central,Timeout
                # Emitted key-value: ("ERR|payment-service", 1)
                yield f"ERR|{service}", 1

            if rt > 800:
                # Example: ...,search-service,/search,...,980,eu-west,ServiceUnavailable
                # Emitted key-value: ("SLOW|search-service,/search", 1)
                yield f"SLOW|{service},{endpoint}", 1
        except Exception:
            pass

    def reducer(self, key, values):
        # Reducer operation: sum([1,1,1,...]) -> total count
        yield key, sum(values)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append(INPUT_PATH)
    
    start = time.time()
    MicroserviceLogAnalysis.run()
    elapsed = time.time() - start
    print(f"MapReduce elapsed: {elapsed:.2f}s", file=sys.stderr)