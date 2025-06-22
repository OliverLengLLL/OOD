from abc import ABC, abstractmethod
from typing import List, Dict, Set, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import re

class Genre(Enum):
    ROCK = "Rock"
    POP = "Pop"
    JAZZ = "Jazz"
    CLASSICAL = "Classical"
    HIP_HOP = "Hip Hop"
    ELECTRONIC = "Electronic"
    COUNTRY = "Country"
    BLUES = "Blues"

@dataclass
class Song:
    """Represents a single song with metadata"""
    id: str
    title: str
    artist: str
    album: str
    genre: Genre
    duration_seconds: int
    release_year: int
    rating: float  # 0-5 stars
    play_count: int = 0
    file_path: str = ""
    
    def __post_init__(self):
        if not (0 <= self.rating <= 5):
            raise ValueError("Rating must be between 0 and 5")
        if self.duration_seconds <= 0:
            raise ValueError("Duration must be positive")

    @property
    def duration_formatted(self) -> str:
        """Return duration in MM:SS format"""
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

class FilterCriteria(ABC):
    """Abstract base class for search filters"""
    
    @abstractmethod
    def matches(self, song: Song) -> bool:
        pass

class TitleFilter(FilterCriteria):
    def __init__(self, title_pattern: str, case_sensitive: bool = False):
        self.title_pattern = title_pattern
        self.case_sensitive = case_sensitive
    
    def matches(self, song: Song) -> bool:
        title = song.title if self.case_sensitive else song.title.lower()
        pattern = self.title_pattern if self.case_sensitive else self.title_pattern.lower()
        return pattern in title

class ArtistFilter(FilterCriteria):
    def __init__(self, artist_name: str, exact_match: bool = False):
        self.artist_name = artist_name
        self.exact_match = exact_match
    
    def matches(self, song: Song) -> bool:
        if self.exact_match:
            return song.artist.lower() == self.artist_name.lower()
        return self.artist_name.lower() in song.artist.lower()

class GenreFilter(FilterCriteria):
    def __init__(self, genres: List[Genre]):
        self.genres = set(genres)
    
    def matches(self, song: Song) -> bool:
        return song.genre in self.genres

class YearRangeFilter(FilterCriteria):
    def __init__(self, start_year: Optional[int] = None, end_year: Optional[int] = None):
        self.start_year = start_year
        self.end_year = end_year
    
    def matches(self, song: Song) -> bool:
        if self.start_year and song.release_year < self.start_year:
            return False
        if self.end_year and song.release_year > self.end_year:
            return False
        return True

class RatingFilter(FilterCriteria):
    def __init__(self, min_rating: float):
        self.min_rating = min_rating
    
    def matches(self, song: Song) -> bool:
        return song.rating >= self.min_rating

class DurationFilter(FilterCriteria):
    def __init__(self, min_duration: Optional[int] = None, max_duration: Optional[int] = None):
        self.min_duration = min_duration
        self.max_duration = max_duration
    
    def matches(self, song: Song) -> bool:
        if self.min_duration and song.duration_seconds < self.min_duration:
            return False
        if self.max_duration and song.duration_seconds > self.max_duration:
            return False
        return True

class CompositeFilter(FilterCriteria):
    """Combines multiple filters with AND logic"""
    def __init__(self, filters: List[FilterCriteria]):
        self.filters = filters
    
    def matches(self, song: Song) -> bool:
        return all(filter_criterion.matches(song) for filter_criterion in self.filters)

class SortCriteria(Enum):
    TITLE = "title"
    ARTIST = "artist"
    ALBUM = "album"
    YEAR = "release_year"
    RATING = "rating"
    DURATION = "duration_seconds"
    PLAY_COUNT = "play_count"

class MusicLibrary:
    """Main music library class with search and filter capabilities"""
    
    def __init__(self):
        self.songs: Dict[str, Song] = {}
        self.artists: Set[str] = set()
        self.albums: Set[str] = set()
        
    def add_song(self, song: Song) -> None:
        """Add a song to the library"""
        if song.id in self.songs:
            raise ValueError(f"Song with ID {song.id} already exists")
        
        self.songs[song.id] = song
        self.artists.add(song.artist)
        self.albums.add(song.album)
    
    def remove_song(self, song_id: str) -> bool:
        """Remove a song from the library"""
        if song_id in self.songs:
            del self.songs[song_id]
            return True
        return False
    
    def get_song(self, song_id: str) -> Optional[Song]:
        """Get a song by ID"""
        return self.songs.get(song_id)
    
    def search(self, 
               filters: List[FilterCriteria] = None,
               sort_by: SortCriteria = SortCriteria.TITLE,
               reverse: bool = False,
               limit: Optional[int] = None) -> List[Song]:
        """Search songs with filters and sorting"""
        
        # Start with all songs
        results = list(self.songs.values())
        
        # Apply filters
        if filters:
            composite_filter = CompositeFilter(filters)
            results = [song for song in results if composite_filter.matches(song)]
        
        # Sort results
        results.sort(key=lambda song: getattr(song, sort_by.value), reverse=reverse)
        
        # Apply limit
        if limit:
            results = results[:limit]
            
        return results
    
    def get_all_artists(self) -> List[str]:
        """Get all unique artists"""
        return sorted(list(self.artists))
    
    def get_all_albums(self) -> List[str]:
        """Get all unique albums"""
        return sorted(list(self.albums))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get library statistics"""
        if not self.songs:
            return {"total_songs": 0}
            
        total_duration = sum(song.duration_seconds for song in self.songs.values())
        avg_rating = sum(song.rating for song in self.songs.values()) / len(self.songs)
        
        genre_counts = {}
        for song in self.songs.values():
            genre_counts[song.genre.value] = genre_counts.get(song.genre.value, 0) + 1
        
        return {
            "total_songs": len(self.songs),
            "total_artists": len(self.artists),
            "total_albums": len(self.albums),
            "total_duration_formatted": f"{total_duration // 3600}:{(total_duration % 3600) // 60:02d}:{total_duration % 60:02d}",
            "average_rating": round(avg_rating, 2),
            "genre_distribution": genre_counts
        }

class PlaylistManager:
    """Manages playlists of songs"""
    
    def __init__(self, library: MusicLibrary):
        self.library = library
        self.playlists: Dict[str, List[str]] = {}  # playlist_name -> list of song_ids
    
    def create_playlist(self, name: str, song_ids: List[str] = None) -> None:
        """Create a new playlist"""
        if name in self.playlists:
            raise ValueError(f"Playlist '{name}' already exists")
        
        # Validate song IDs
        if song_ids:
            for song_id in song_ids:
                if song_id not in self.library.songs:
                    raise ValueError(f"Song ID '{song_id}' not found in library")
        
        self.playlists[name] = song_ids or []
    
    def add_to_playlist(self, playlist_name: str, song_id: str) -> None:
        """Add a song to a playlist"""
        if playlist_name not in self.playlists:
            raise ValueError(f"Playlist '{playlist_name}' does not exist")
        
        if song_id not in self.library.songs:
            raise ValueError(f"Song ID '{song_id}' not found in library")
        
        if song_id not in self.playlists[playlist_name]:
            self.playlists[playlist_name].append(song_id)
    
    def get_playlist_songs(self, playlist_name: str) -> List[Song]:
        """Get all songs in a playlist"""
        if playlist_name not in self.playlists:
            raise ValueError(f"Playlist '{playlist_name}' does not exist")
        
        return [self.library.songs[song_id] for song_id in self.playlists[playlist_name]]

# Demo usage
def main():
    # Create library
    library = MusicLibrary()
    
    # Add sample songs
    songs = [
        Song("1", "Bohemian Rhapsody", "Queen", "A Night at the Opera", Genre.ROCK, 355, 1975, 4.9),
        Song("2", "Billie Jean", "Michael Jackson", "Thriller", Genre.POP, 294, 1982, 4.8),
        Song("3", "Take Five", "Dave Brubeck", "Time Out", Genre.JAZZ, 324, 1959, 4.7),
        Song("4", "Hotel California", "Eagles", "Hotel California", Genre.ROCK, 391, 1976, 4.8),
        Song("5", "Lose Yourself", "Eminem", "8 Mile Soundtrack", Genre.HIP_HOP, 326, 2002, 4.6),
        Song("6", "Shape of You", "Ed Sheeran", "÷ (Divide)", Genre.POP, 233, 2017, 4.2),
        Song("7", "Stairway to Heaven", "Led Zeppelin", "Led Zeppelin IV", Genre.ROCK, 482, 1971, 4.9),
    ]
    
    for song in songs:
        library.add_song(song)
    
    print("=== Music Library Demo ===\n")
    
    # Basic search - all songs
    print("All songs:")
    all_songs = library.search()
    for song in all_songs:
        print(f"  {song.title} by {song.artist} ({song.release_year})")
    
    print(f"\n=== Search Examples ===")
    
    # Search by artist
    print("\nRock songs:")
    rock_songs = library.search([GenreFilter([Genre.ROCK])])
    for song in rock_songs:
        print(f"  {song.title} by {song.artist}")
    
    # Search by year range and rating
    print("\nSongs from 1970-1980 with rating >= 4.8:")
    classic_hits = library.search([
        YearRangeFilter(1970, 1980),
        RatingFilter(4.8)
    ])
    for song in classic_hits:
        print(f"  {song.title} by {song.artist} ({song.release_year}) - ⭐{song.rating}")
    
    # Search by artist with partial match
    print("\nSongs by artists containing 'E':")
    e_artists = library.search([ArtistFilter("E")], sort_by=SortCriteria.ARTIST)
    for song in e_artists:
        print(f"  {song.title} by {song.artist}")
    
    # Search by duration
    print("\nSongs longer than 5 minutes:")
    long_songs = library.search([DurationFilter(min_duration=300)], 
                               sort_by=SortCriteria.DURATION, reverse=True)
    for song in long_songs:
        print(f"  {song.title} - {song.duration_formatted}")
    
    # Library stats
    print(f"\n=== Library Statistics ===")
    stats = library.get_stats()
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Playlist demo
    print(f"\n=== Playlist Demo ===")
    playlist_manager = PlaylistManager(library)
    playlist_manager.create_playlist("My Favorites", ["1", "4", "7"])  # Rock classics
    
    favorite_songs = playlist_manager.get_playlist_songs("My Favorites")
    print("My Favorites playlist:")
    for song in favorite_songs:
        print(f"  {song.title} by {song.artist}")

if __name__ == "__main__":
    main()