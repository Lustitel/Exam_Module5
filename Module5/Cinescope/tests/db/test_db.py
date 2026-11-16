
class TestDBUser:

    def test_db_requests(self, super_admin, db_helper, created_test_user, db_user_data):
        assert not db_helper.user_exists_by_email(db_user_data["email"])
        assert created_test_user == db_helper.get_user_by_id(created_test_user.id)
        assert db_helper.user_exists_by_email("api1@gmail.com")

class TestDBMovies:

    def test_db_request_movie_life_circle(self, super_admin, db_helper, test_film):
        movie_name = test_film["name"]
        assert not db_helper.movie_exists_by_name(movie_name)

        new_created_movie = super_admin.api.movies_api.create_movie(test_film)
        new_movie_id = new_created_movie.json()["id"]
        movie_in_db = db_helper.get_movie_by_id(new_movie_id)
        assert movie_in_db is not None
        assert movie_in_db == db_helper.get_movie_by_id(movie_in_db.id)
        assert db_helper.movie_exists_by_name(movie_in_db.name)

        super_admin.api.movies_api.delete_movie(new_movie_id)
        assert db_helper.get_movie_by_name(movie_name) is None



