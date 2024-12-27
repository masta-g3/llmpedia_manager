import os
import pandas as pd
from datetime import datetime, timedelta
import tweepy
from dotenv import load_dotenv
import time

def load_twitter_credentials():
    """Load Twitter API credentials from environment variables."""
    load_dotenv()
    
    required_vars = [
        'TWITTER_CONSUMER_KEY',
        'TWITTER_CONSUMER_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'TWITTER_BEARER_TOKEN'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {var: os.getenv(var) for var in required_vars}

def get_twitter_client():
    """Initialize and return authenticated Twitter client."""
    creds = load_twitter_credentials()
    
    # Initialize client with OAuth 1.0a User Context and Bearer Token
    client = tweepy.Client(
        bearer_token=creds['TWITTER_BEARER_TOKEN'],
        consumer_key=creds['TWITTER_CONSUMER_KEY'],
        consumer_secret=creds['TWITTER_CONSUMER_SECRET'],
        access_token=creds['TWITTER_ACCESS_TOKEN'],
        access_token_secret=creds['TWITTER_ACCESS_TOKEN_SECRET']
    )
    
    return client

def fetch_tweet_metrics(client, start_time=None, end_time=None):
    """Fetch tweet metrics for the specified time period."""
    if not start_time:
        start_time = datetime.now() - timedelta(days=90)  # Last 90 days
    if not end_time:
        end_time = datetime.now()
    
    # Get user's tweets
    tweets = []
    pagination_token = None
    
    while True:
        try:
            # First, get the authenticated user's ID
            user_response = client.get_me()
            if not user_response.data:
                raise ValueError("Could not get authenticated user information")
            user_id = user_response.data.id
            
            # Then get the tweets with exponential backoff for rate limits
            max_retries = 5
            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = client.get_users_tweets(
                        id=user_id,
                        tweet_fields=['created_at', 'public_metrics', 'text'],
                        start_time=start_time,
                        end_time=end_time,
                        pagination_token=pagination_token,
                        max_results=100
                    )
                    break  # If successful, break the retry loop
                except tweepy.TooManyRequests as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise e
                    # Wait with exponential backoff
                    wait_time = 2 ** retry_count * 60  # Wait 2, 4, 8, 16 minutes
                    print(f"Rate limit reached. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
            
            if not response.data:
                break
                
            tweets.extend(response.data)
            
            if not response.meta.get('next_token'):
                break
                
            pagination_token = response.meta['next_token']
            
            # Add a small delay between requests to avoid hitting rate limits
            time.sleep(2)
            
        except tweepy.TooManyRequests as e:
            print(f"Rate limit exceeded. Please try again later.")
            raise e
        except Exception as e:
            print(f"Error fetching tweets: {str(e)}")
            raise e
    
    # Convert to DataFrame
    tweet_data = []
    for tweet in tweets:
        metrics = tweet.public_metrics
        tweet_data.append({
            'Post id': tweet.id,
            'Date': tweet.created_at,
            'Post text': tweet.text,
            'Link': f"https://x.com/user/status/{tweet.id}",
            'Impressions': metrics.get('impression_count', 0),
            'Likes': metrics.get('like_count', 0),
            'Engagements': sum([
                metrics.get('like_count', 0),
                metrics.get('reply_count', 0),
                metrics.get('retweet_count', 0),
                metrics.get('quote_count', 0)
            ]),
            'Bookmarks': metrics.get('bookmark_count', 0),
            'Share': metrics.get('quote_count', 0),
            'New follows': 0,  # Not available in API
            'Replies': metrics.get('reply_count', 0),
            'Reposts': metrics.get('retweet_count', 0),
            'Profile visits': 0,  # Not available in API
            'Detail expands': 0,  # Not available in API
            'Url clicks': 0,  # Not available in API
            'Hashtag clicks': 0,  # Not available in API
            'Permalink clicks': 0  # Not available in API
        })
    
    df = pd.DataFrame(tweet_data)
    return df

def save_analytics(df, output_file='data/account_analytics_content.csv'):
    """Save analytics data to CSV file."""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # If file exists, merge with existing data
    if os.path.exists(output_file):
        existing_df = pd.read_csv(output_file)
        # Convert date columns to datetime
        existing_df['Date'] = pd.to_datetime(existing_df['Date'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Combine and remove duplicates, keeping newer data
        combined_df = pd.concat([existing_df, df])
        combined_df = combined_df.drop_duplicates(subset='Post id', keep='last')
        combined_df = combined_df.sort_values('Date', ascending=False)
        df = combined_df
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Analytics data saved to {output_file}")

def main():
    """Main function to fetch and save Twitter analytics."""
    try:
        client = get_twitter_client()
        print("Successfully authenticated with Twitter API")
        
        # Fetch last 90 days of data
        print("Fetching tweet metrics...")
        df = fetch_tweet_metrics(client)
        
        # Save the data
        save_analytics(df)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 