import pandas as pd
import re

def identify_threads(df):
    """Identify threads in the tweet data."""
    # Read the CSV file
    df = pd.read_csv('data/account_analytics_content_2024-12-25.csv')
    
    # Initialize thread role columns
    df['is_thread_start'] = False
    df['is_link_tweet'] = False
    df['is_discussion_tweet'] = False
    df['thread_id'] = None
    
    # Pattern to match dates like (Dec 19, 2024) or similar
    date_pattern = r'\([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\)'
    
    # First pass: Mark all tweets with their roles
    for i, row in df.iterrows():
        text = str(row['Post text']) if pd.notna(row['Post text']) else ''
        
        # Check for thread start (contains a date)
        if re.search(date_pattern, text):
            df.loc[i, 'is_thread_start'] = True
        
        # Check for links
        if 'arxiv link:' in text.lower() and 'llmpedia link:' in text.lower():
            df.loc[i, 'is_link_tweet'] = True
        
        # Check for discussion
        if 'related discussion:' in text.lower() or 'repo:' in text.lower():
            df.loc[i, 'is_discussion_tweet'] = True
    
    # Count different types of tweets
    date_tweets = df['is_thread_start'].sum()
    link_tweets = df['is_link_tweet'].sum()
    discussion_tweets = df['is_discussion_tweet'].sum()
    
    print(f"\nTweet type counts:")
    print(f"Tweets with dates: {date_tweets}")
    print(f"Tweets with arxiv/llmpedia links: {link_tweets}")
    print(f"Tweets with related discussion: {discussion_tweets}")
    
    # Second pass: Group tweets into threads
    thread_id = 0
    threads = []
    i = 0
    
    while i < len(df):
        if df.iloc[i]['is_thread_start']:
            thread_id += 1
            current_thread = [df.iloc[i].to_dict()]
            df.loc[df.index[i], 'thread_id'] = thread_id
            
            # Look ahead for related tweets (up to 5 positions)
            look_ahead = min(i + 5, len(df))
            found_link = False
            found_discussion = False
            
            for j in range(i + 1, look_ahead):
                next_tweet = df.iloc[j]
                
                # Look for link tweet first
                if not found_link and next_tweet['is_link_tweet']:
                    current_thread.append(next_tweet.to_dict())
                    df.loc[df.index[j], 'thread_id'] = thread_id
                    found_link = True
                    continue
                
                # Then look for discussion tweet
                if found_link and not found_discussion and next_tweet['is_discussion_tweet']:
                    current_thread.append(next_tweet.to_dict())
                    df.loc[df.index[j], 'thread_id'] = thread_id
                    found_discussion = True
                    break
            
            if found_link:  # Add thread even if no discussion tweet found
                threads.append(current_thread)
            i = j + 1 if found_link else i + 1
        else:
            i += 1
    
    # Print statistics
    print(f"\nThread statistics:")
    print(f"Total threads found: {len(threads)}")
    if threads:
        print(f"Average tweets per thread: {sum(len(t) for t in threads) / len(threads):.1f}")
        
        # Count threads by size
        thread_sizes = {}
        for thread in threads:
            size = len(thread)
            thread_sizes[size] = thread_sizes.get(size, 0) + 1
        
        print("\nThread size distribution:")
        for size in sorted(thread_sizes.keys()):
            print(f"{size} tweets: {thread_sizes[size]} threads")
    
    # Save the processed data
    df.to_csv('data/account_analytics_content.csv', index=False)
    print("\nProcessed data saved to data/account_analytics_content.csv")
    
    return df

if __name__ == "__main__":
    identify_threads(None)  # df parameter not used anymore 