"""
Public Dataset ETL Pipeline - Task 7
Demonstrates ETL adaptability with external datasets

Datasets used:
1. Iris Dataset (clean, normalized) - Classic ML dataset
2. Movies Dataset (messy JSON) - Requires more transformation
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
import requests
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# LOGGING SETUP
# ============================================

def setup_logging():
    """Configure logging"""
    log_dir = 'etl/logs'
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'public_datasets_{timestamp}.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__), log_file

logger, log_file = setup_logging()

# ============================================
# DATABASE CONNECTION
# ============================================

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', 5432)
    )

# ============================================
# DATASET 1: IRIS DATASET (Clean/Normalized)
# ============================================

class IrisDatasetETL:
    """
    ETL for Iris Dataset
    Source: UCI Machine Learning Repository
    This is a clean, well-structured dataset
    """

    DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"

    def __init__(self):
        self.columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']

    def create_schema(self, conn):
        """Create iris table schema"""
        cursor = conn.cursor()

        cursor.execute("""
            DROP TABLE IF EXISTS iris_data CASCADE;

            CREATE TABLE iris_data (
                id SERIAL PRIMARY KEY,
                sepal_length DECIMAL(3,1) NOT NULL,
                sepal_width DECIMAL(3,1) NOT NULL,
                petal_length DECIMAL(3,1) NOT NULL,
                petal_width DECIMAL(3,1) NOT NULL,
                species VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Index for species queries
            CREATE INDEX idx_iris_species ON iris_data(species);
        """)

        conn.commit()
        cursor.close()
        logger.info("Iris table schema created")

    def extract(self) -> pd.DataFrame:
        """Extract data from UCI repository"""
        logger.info(f"Extracting Iris dataset from {self.DATASET_URL}")

        try:
            df = pd.read_csv(self.DATASET_URL, header=None, names=self.columns)
            logger.info(f"Extracted {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Failed to extract Iris dataset: {e}")
            # Fallback to local sample
            return self._create_sample_data()

    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample data if URL fails"""
        logger.info("Using sample Iris data")
        data = [
            [5.1, 3.5, 1.4, 0.2, 'Iris-setosa'],
            [4.9, 3.0, 1.4, 0.2, 'Iris-setosa'],
            [7.0, 3.2, 4.7, 1.4, 'Iris-versicolor'],
            [6.4, 3.2, 4.5, 1.5, 'Iris-versicolor'],
            [6.3, 3.3, 6.0, 2.5, 'Iris-virginica'],
            [5.8, 2.7, 5.1, 1.9, 'Iris-virginica']
        ]
        return pd.DataFrame(data, columns=self.columns)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform Iris data (minimal transformation needed)"""
        logger.info("Transforming Iris data")

        # Remove any rows with missing values
        initial_count = len(df)
        df = df.dropna()
        removed = initial_count - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} rows with missing values")

        # Clean species names
        df['species'] = df['species'].str.strip()

        return df

    def load(self, df: pd.DataFrame, conn) -> Dict:
        """Load data into database"""
        logger.info("Loading Iris data into database")

        cursor = conn.cursor()
        inserted = 0
        errors = []

        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO iris_data (sepal_length, sepal_width, petal_length, petal_width, species)
                    VALUES (%s, %s, %s, %s, %s)
                """, (row['sepal_length'], row['sepal_width'], row['petal_length'],
                      row['petal_width'], row['species']))
                inserted += 1
            except Exception as e:
                errors.append(str(e))

        conn.commit()
        cursor.close()

        return {'inserted': inserted, 'errors': errors}

    def run(self) -> Dict:
        """Execute full ETL pipeline"""
        logger.info("=" * 60)
        logger.info("IRIS DATASET ETL")
        logger.info("=" * 60)

        start_time = datetime.now()

        conn = get_db_connection()

        try:
            # Create schema
            self.create_schema(conn)

            # ETL
            df = self.extract()
            df = self.transform(df)
            load_stats = self.load(df, conn)

            duration = (datetime.now() - start_time).total_seconds()

            report = {
                'dataset': 'Iris',
                'status': 'SUCCESS',
                'records_extracted': len(df),
                'records_loaded': load_stats['inserted'],
                'errors': load_stats['errors'],
                'duration_seconds': duration
            }

            logger.info(f"Iris ETL completed: {load_stats['inserted']} records in {duration:.2f}s")

        except Exception as e:
            report = {'dataset': 'Iris', 'status': 'FAILED', 'error': str(e)}
            logger.error(f"Iris ETL failed: {e}")

        finally:
            conn.close()

        return report

# ============================================
# DATASET 2: MOVIES DATASET (Messy JSON)
# ============================================

class MoviesDatasetETL:
    """
    ETL for Movies Dataset
    Source: Sample movie data (simulating messy JSON)
    Demonstrates handling of:
    - Nested JSON
    - Missing values
    - Data type conversions
    - Duplicates
    """

    def __init__(self):
        pass

    def create_schema(self, conn):
        """Create movies table schema"""
        cursor = conn.cursor()

        cursor.execute("""
            DROP TABLE IF EXISTS movies CASCADE;
            DROP TABLE IF EXISTS movie_genres CASCADE;

            -- Main movies table
            CREATE TABLE movies (
                movie_id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                release_year INTEGER,
                runtime_minutes INTEGER,
                rating DECIMAL(3,1),
                votes INTEGER,
                director VARCHAR(200),
                budget_usd BIGINT,
                revenue_usd BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Genres table (normalized)
            CREATE TABLE movie_genres (
                id SERIAL PRIMARY KEY,
                movie_id INTEGER REFERENCES movies(movie_id) ON DELETE CASCADE,
                genre VARCHAR(50) NOT NULL
            );

            -- Indexes
            CREATE INDEX idx_movies_year ON movies(release_year);
            CREATE INDEX idx_movies_rating ON movies(rating);
            CREATE INDEX idx_movie_genres_movie ON movie_genres(movie_id);
            CREATE INDEX idx_movie_genres_genre ON movie_genres(genre);
        """)

        conn.commit()
        cursor.close()
        logger.info("Movies table schema created")

    def extract(self) -> List[Dict]:
        """Extract movie data (using sample data or URL)"""
        logger.info("Extracting Movies dataset")

        # Sample messy movie data
        movies = [
            {
                "title": "The Shawshank Redemption",
                "year": "1994",
                "runtime": "142 min",
                "rating": 9.3,
                "votes": "2,500,000",
                "genres": ["Drama"],
                "director": "Frank Darabont"
            },
            {
                "title": "The Dark Knight",
                "year": 2008,
                "runtime": 152,
                "rating": "9.0",
                "votes": 2400000,
                "genres": ["Action", "Crime", "Drama"],
                "director": "Christopher Nolan",
                "budget": "$185,000,000",
                "revenue": "$1,005,000,000"
            },
            {
                "title": "Inception",
                "year": "2010",
                "runtime": "148",
                "rating": 8.8,
                "votes": "2,100,000",
                "genres": ["Action", "Sci-Fi", "Thriller"],
                "director": "Christopher Nolan"
            },
            {
                "title": "Pulp Fiction",
                "year": 1994,
                "runtime": "154 minutes",
                "rating": 8.9,
                "genres": "Crime, Drama",  # String instead of list
                "director": "Quentin Tarantino"
            },
            {
                "title": "Fight Club",
                "year": "1999",
                "runtime": 139,
                "rating": "8.8",
                "votes": None,  # Missing
                "genres": ["Drama"],
                "director": "David Fincher"
            },
            {
                "title": "The Matrix",
                "year": 1999,
                "runtime": "136 min",
                "rating": 8.7,
                "genres": ["Action", "Sci-Fi"],
                "director": "Lana Wachowski"
            },
            {
                "title": "The Matrix",  # Duplicate!
                "year": "1999",
                "runtime": 136,
                "rating": 8.7,
                "genres": ["Sci-Fi", "Action"],
                "director": "Lilly Wachowski"
            },
            {
                "title": "Interstellar",
                "year": 2014,
                "runtime": "169 min",
                "rating": "8.6",
                "genres": ["Adventure", "Drama", "Sci-Fi"],
                "director": "Christopher Nolan",
                "budget": "165000000",
                "revenue": "677471339"
            },
            {
                "title": "",  # Missing title
                "year": 2020,
                "rating": 7.5
            },
            {
                "title": "Parasite",
                "year": "2019",
                "runtime": "132",
                "rating": 8.6,
                "genres": ["Comedy", "Drama", "Thriller"],
                "director": "Bong Joon-ho"
            }
        ]

        logger.info(f"Extracted {len(movies)} raw movie records")
        return movies

    def transform(self, movies: List[Dict]) -> Tuple[pd.DataFrame, List[Dict]]:
        """Transform messy movie data"""
        logger.info("Transforming Movies data")

        cleaned_movies = []
        genres_data = []
        seen_titles = set()

        for movie in movies:
            # Skip if no title
            title = movie.get('title', '').strip()
            if not title:
                logger.warning("Skipping movie with missing title")
                continue

            # Skip duplicates
            title_key = title.lower()
            if title_key in seen_titles:
                logger.warning(f"Skipping duplicate: {title}")
                continue
            seen_titles.add(title_key)

            # Clean year
            year = self._clean_year(movie.get('year'))

            # Clean runtime
            runtime = self._clean_runtime(movie.get('runtime'))

            # Clean rating
            rating = self._clean_rating(movie.get('rating'))

            # Clean votes
            votes = self._clean_votes(movie.get('votes'))

            # Clean budget/revenue
            budget = self._clean_money(movie.get('budget'))
            revenue = self._clean_money(movie.get('revenue'))

            cleaned_movie = {
                'title': title,
                'release_year': year,
                'runtime_minutes': runtime,
                'rating': rating,
                'votes': votes,
                'director': movie.get('director', '').strip() or None,
                'budget_usd': budget,
                'revenue_usd': revenue
            }

            cleaned_movies.append(cleaned_movie)

            # Extract genres
            raw_genres = movie.get('genres', [])
            if isinstance(raw_genres, str):
                raw_genres = [g.strip() for g in raw_genres.split(',')]

            for genre in raw_genres:
                if genre:
                    genres_data.append({
                        'title': title,
                        'genre': genre.strip()
                    })

        df_movies = pd.DataFrame(cleaned_movies)
        logger.info(f"Transformed {len(df_movies)} movies with {len(genres_data)} genre mappings")

        return df_movies, genres_data

    def _clean_year(self, year) -> int:
        """Clean year field"""
        if not year:
            return None
        try:
            return int(str(year).strip())
        except:
            return None

    def _clean_runtime(self, runtime) -> int:
        """Clean runtime field (handles '142 min', '142', etc.)"""
        if not runtime:
            return None
        try:
            runtime_str = str(runtime).lower().replace('min', '').replace('minutes', '').strip()
            return int(float(runtime_str))
        except:
            return None

    def _clean_rating(self, rating) -> float:
        """Clean rating field"""
        if not rating:
            return None
        try:
            return round(float(str(rating).strip()), 1)
        except:
            return None

    def _clean_votes(self, votes) -> int:
        """Clean votes field (handles '2,500,000' format)"""
        if not votes:
            return None
        try:
            votes_str = str(votes).replace(',', '').strip()
            return int(float(votes_str))
        except:
            return None

    def _clean_money(self, money) -> int:
        """Clean budget/revenue (handles '$185,000,000' format)"""
        if not money:
            return None
        try:
            money_str = str(money).replace('$', '').replace(',', '').strip()
            return int(float(money_str))
        except:
            return None

    def load(self, df_movies: pd.DataFrame, genres_data: List[Dict], conn) -> Dict:
        """Load movies and genres into database"""
        logger.info("Loading Movies data into database")

        cursor = conn.cursor()
        inserted_movies = 0
        inserted_genres = 0
        errors = []

        # Insert movies
        movie_id_map = {}

        for _, row in df_movies.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO movies (title, release_year, runtime_minutes, rating, votes,
                                       director, budget_usd, revenue_usd)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING movie_id
                """, (row['title'], row['release_year'], row['runtime_minutes'],
                      row['rating'], row['votes'], row['director'],
                      row['budget_usd'], row['revenue_usd']))

                movie_id = cursor.fetchone()[0]
                movie_id_map[row['title']] = movie_id
                inserted_movies += 1

            except Exception as e:
                errors.append(f"Movie '{row['title']}': {str(e)}")

        # Insert genres
        for genre_entry in genres_data:
            try:
                movie_id = movie_id_map.get(genre_entry['title'])
                if movie_id:
                    cursor.execute("""
                        INSERT INTO movie_genres (movie_id, genre)
                        VALUES (%s, %s)
                    """, (movie_id, genre_entry['genre']))
                    inserted_genres += 1

            except Exception as e:
                errors.append(f"Genre for '{genre_entry['title']}': {str(e)}")

        conn.commit()
        cursor.close()

        return {
            'movies_inserted': inserted_movies,
            'genres_inserted': inserted_genres,
            'errors': errors
        }

    def run(self) -> Dict:
        """Execute full ETL pipeline"""
        logger.info("=" * 60)
        logger.info("MOVIES DATASET ETL")
        logger.info("=" * 60)

        start_time = datetime.now()

        conn = get_db_connection()

        try:
            # Create schema
            self.create_schema(conn)

            # ETL
            raw_data = self.extract()
            df_movies, genres_data = self.transform(raw_data)
            load_stats = self.load(df_movies, genres_data, conn)

            duration = (datetime.now() - start_time).total_seconds()

            report = {
                'dataset': 'Movies',
                'status': 'SUCCESS',
                'raw_records': len(raw_data),
                'movies_loaded': load_stats['movies_inserted'],
                'genres_loaded': load_stats['genres_inserted'],
                'errors': load_stats['errors'],
                'duration_seconds': duration
            }

            logger.info(f"Movies ETL completed: {load_stats['movies_inserted']} movies, "
                       f"{load_stats['genres_inserted']} genres in {duration:.2f}s")

        except Exception as e:
            report = {'dataset': 'Movies', 'status': 'FAILED', 'error': str(e)}
            logger.error(f"Movies ETL failed: {e}")

        finally:
            conn.close()

        return report

# ============================================
# OPTIMIZATION QUERIES
# ============================================

def run_optimization_demo(conn):
    """Demonstrate query optimization techniques"""
    logger.info("=" * 60)
    logger.info("QUERY OPTIMIZATION DEMO")
    logger.info("=" * 60)

    cursor = conn.cursor()

    queries = [
        # Query 1: Simple indexed query
        {
            'name': 'Iris by Species (indexed)',
            'sql': "SELECT * FROM iris_data WHERE species = 'Iris-setosa'"
        },
        # Query 2: Aggregation
        {
            'name': 'Iris Species Statistics',
            'sql': """
                SELECT
                    species,
                    COUNT(*) as count,
                    ROUND(AVG(sepal_length)::numeric, 2) as avg_sepal_length,
                    ROUND(AVG(petal_length)::numeric, 2) as avg_petal_length
                FROM iris_data
                GROUP BY species
            """
        },
        # Query 3: Movies with genres (JOIN)
        {
            'name': 'Movies with Genres',
            'sql': """
                SELECT
                    m.title,
                    m.release_year,
                    m.rating,
                    STRING_AGG(g.genre, ', ') as genres
                FROM movies m
                LEFT JOIN movie_genres g ON m.movie_id = g.movie_id
                GROUP BY m.movie_id, m.title, m.release_year, m.rating
                ORDER BY m.rating DESC
            """
        },
        # Query 4: Genre popularity
        {
            'name': 'Genre Popularity',
            'sql': """
                SELECT
                    genre,
                    COUNT(*) as movie_count,
                    ROUND(AVG(m.rating)::numeric, 2) as avg_rating
                FROM movie_genres g
                JOIN movies m ON g.movie_id = m.movie_id
                GROUP BY genre
                ORDER BY movie_count DESC
            """
        }
    ]

    results = []

    for query in queries:
        try:
            # Run EXPLAIN ANALYZE
            start = datetime.now()
            cursor.execute(f"EXPLAIN ANALYZE {query['sql']}")
            explain_result = cursor.fetchall()
            exec_time = (datetime.now() - start).total_seconds() * 1000

            # Run actual query
            cursor.execute(query['sql'])
            rows = cursor.fetchall()

            results.append({
                'query': query['name'],
                'rows_returned': len(rows),
                'execution_time_ms': exec_time,
                'uses_index': 'Index' in str(explain_result)
            })

            logger.info(f"\n{query['name']}:")
            logger.info(f"  Rows: {len(rows)}, Time: {exec_time:.2f}ms, Uses Index: {'Yes' if 'Index' in str(explain_result) else 'No'}")

        except Exception as e:
            logger.error(f"Query '{query['name']}' failed: {e}")

    cursor.close()
    return results

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Run all public dataset ETL pipelines"""

    logger.info("=" * 60)
    logger.info("PUBLIC DATASETS ETL PIPELINE")
    logger.info("Task 7: Demonstrating ETL Adaptability")
    logger.info("=" * 60)

    start_time = datetime.now()
    reports = []

    # Dataset 1: Iris (Clean)
    iris_etl = IrisDatasetETL()
    reports.append(iris_etl.run())

    # Dataset 2: Movies (Messy)
    movies_etl = MoviesDatasetETL()
    reports.append(movies_etl.run())

    # Run optimization demo
    logger.info("\nRunning optimization demos...")
    try:
        conn = get_db_connection()
        optimization_results = run_optimization_demo(conn)
        conn.close()
    except Exception as e:
        logger.error(f"Optimization demo failed: {e}")
        optimization_results = []

    # Final report
    total_duration = (datetime.now() - start_time).total_seconds()

    logger.info("\n" + "=" * 60)
    logger.info("FINAL REPORT")
    logger.info("=" * 60)

    for report in reports:
        logger.info(f"\n{report['dataset']} Dataset:")
        logger.info(f"  Status: {report['status']}")
        if report['status'] == 'SUCCESS':
            if 'records_loaded' in report:
                logger.info(f"  Records Loaded: {report['records_loaded']}")
            if 'movies_loaded' in report:
                logger.info(f"  Movies Loaded: {report['movies_loaded']}")
                logger.info(f"  Genres Loaded: {report['genres_loaded']}")
            logger.info(f"  Duration: {report['duration_seconds']:.2f}s")

    logger.info(f"\nTotal Duration: {total_duration:.2f}s")
    logger.info(f"Log file: {log_file}")

    return reports

if __name__ == "__main__":
    main()
