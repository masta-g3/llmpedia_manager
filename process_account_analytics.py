import pandas as pd
import re
from pathlib import Path
from datetime import datetime


def get_analytics_files():
    """Get all analytics files sorted by date (newest first)."""
    data_dir = Path("data")
    files = []
    pattern = r"account_analytics_content_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2}).csv"

    for f in data_dir.glob("account_analytics_content_*.csv"):
        match = re.match(pattern, f.name)
        if match:
            # Use end date from date range
            date = datetime.strptime(match.group(2), "%Y-%m-%d")
            files.append((date, f))

    return [f for _, f in sorted(files, reverse=True)]


def identify_threads():
    """Identify threads in the tweet data across multiple files."""
    analytics_files = get_analytics_files()
    if not analytics_files:
        raise ValueError("No analytics files found in data directory")

    all_threads = {}  # Dict to store latest version of each thread
    all_df = pd.DataFrame()  # Combined dataframe
    global_thread_id = 0  # Keep track across files

    for file_path in analytics_files:
        print(f"\nProcessing file: {file_path}")
        df = pd.read_csv(file_path)

        # Convert Date column to datetime
        df["Date"] = pd.to_datetime(df["Date"])
        
        # Reverse the DataFrame to get chronological order
        df = df.iloc[::-1].reset_index(drop=True)

        # Print input file statistics
        print("\nInput file statistics:")
        print(f"Total number of tweets: {len(df)}")
        print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")

        # Initialize thread role columns
        df["is_thread_start"] = False
        df["is_link_tweet"] = False
        df["is_discussion_tweet"] = False
        df["thread_id"] = None

        # Pattern to match dates like (Dec 19, 2024) or similar
        date_pattern = r"\([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\)"

        # Mark all tweets with their roles
        for i, row in df.iterrows():
            text = str(row["Post text"]) if pd.notna(row["Post text"]) else ""

            if re.search(date_pattern, text):
                df.loc[i, "is_thread_start"] = True
            if "arxiv link:" in text.lower() and "llmpedia link:" in text.lower():
                df.loc[i, "is_link_tweet"] = True
            if "related discussion:" in text.lower() or "repo:" in text.lower():
                df.loc[i, "is_discussion_tweet"] = True

        # Group tweets into threads
        i = 0
        while i < len(df):
            if df.iloc[i]["is_thread_start"]:
                global_thread_id += 1
                current_thread = [df.iloc[i].to_dict()]
                df.loc[df.index[i], "thread_id"] = global_thread_id

                look_ahead = min(i + 5, len(df))
                found_link = False
                found_discussion = False

                for j in range(i + 1, look_ahead):
                    next_tweet = df.iloc[j]

                    if not found_link and next_tweet["is_link_tweet"]:
                        current_thread.append(next_tweet.to_dict())
                        df.loc[df.index[j], "thread_id"] = global_thread_id
                        found_link = True
                        continue

                    if (
                        found_link
                        and not found_discussion
                        and next_tweet["is_discussion_tweet"]
                    ):
                        current_thread.append(next_tweet.to_dict())
                        df.loc[df.index[j], "thread_id"] = global_thread_id
                        found_discussion = True
                        break

                if found_link:
                    # Use the first tweet's ID as thread identifier
                    thread_key = current_thread[0]["Post id"]
                    # Get the most recent tweet date in the current thread
                    current_thread_date = max(
                        pd.to_datetime(tweet["Date"]) for tweet in current_thread
                    )

                    # Update thread if it's new or more recent than existing version
                    if thread_key not in all_threads:
                        all_threads[thread_key] = current_thread
                    else:
                        existing_thread_date = max(
                            pd.to_datetime(tweet["Date"])
                            for tweet in all_threads[thread_key]
                        )
                        if current_thread_date > existing_thread_date:
                            all_threads[thread_key] = current_thread

                i = j + 1 if found_link else i + 1
            else:
                i += 1

        # Combine with previous data
        all_df = pd.concat([all_df, df], ignore_index=True)

    # Drop duplicates keeping latest version based on Date
    all_df = all_df.drop_duplicates(subset="Post id", keep="first")

    # Print final statistics
    print("\nFinal Thread Statistics:")
    print(f"Total unique threads found: {len(all_threads)}")
    if all_threads:
        avg_tweets = sum(len(t) for t in all_threads.values()) / len(all_threads)
        print(f"Average tweets per thread: {avg_tweets:.1f}")

        # Count threads by size
        thread_sizes = {}
        for thread in all_threads.values():
            size = len(thread)
            thread_sizes[size] = thread_sizes.get(size, 0) + 1

        print("\nThread size distribution:")
        for size in sorted(thread_sizes.keys()):
            print(f"{size} tweets: {thread_sizes[size]} threads")

    # Save the processed data
    output_file = "data/account_analytics_content.csv"
    all_df.to_csv(output_file, index=False)
    print(f"\nProcessed data saved to {output_file}")

    return all_df


if __name__ == "__main__":
    identify_threads()
