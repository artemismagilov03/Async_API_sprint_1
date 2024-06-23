from enum import StrEnum


class FilmSortOption(StrEnum):
    id = 'id'
    neg_id = '-id'

    title = 'title'
    neg_title = '-title'


class GenreSortOption(StrEnum):
    id = 'id'
    neg_id = '-id'

    name = 'name'
    neg_name = '-name'
