from enum import StrEnum


class FilmSortOption(StrEnum):
    id = 'id'
    neg_id = '-id'

    title = 'title'
    neg_title = '-title'

    imdb_rating = 'rating'
    neg_imdb_rating = '-rating'


class GenreSortOption(StrEnum):
    id = 'id'
    neg_id = '-id'

    name = 'name'
    neg_name = '-name'


class PersonSortOption(StrEnum):
    id = 'id'
    neg_id = '-id'

    full_name = 'full_name'
    neg_full_name = '-full_name'
