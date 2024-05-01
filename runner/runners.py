from database import engine
from flask import Blueprint, session, request, jsonify
from strings import *
from sqlalchemy import text

# from auth.auth import logged_in

runners = Blueprint("runners", __name__)


@runners.route("/")
# @logged_in
def get_all_runners():

    runners = []
    with engine.connect() as conn:

        query = text("SELECT * FROM runner")

        result = conn.execute(query)

        if not result:
            response = jsonify(NO_RUNNERS)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 404

        else:
            for row in result:
                runners.append(dict(row._mapping))

                response = jsonify(RUNNERS_FETCHED, {"data": runners})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 200


@runners.route("/<id>")
# @logged_in
def get_one_runner(id):

    with engine.connect() as conn:

        query = text("SELECT * FROM runner where id = :id")
        params = dict(id=id)

        result = conn.execute(query, params).fetchone()

        if result is None:
            response = jsonify(NO_SINGLE_RUNNER)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 404

        else:
            response = jsonify(ONE_RUNNER_FETHCED, {"data": dict(result)})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 200


# @logged_in
@runners.route("/<event_id>/registration", methods=["GET", "POST"])
def registration(event_id):

    if request.method == "POST":

        counter = 0
        data = request.form

        if not data["first_name"]:
            response = jsonify(FIRST_NAME_EMPTY)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 404

        elif not data["last_name"]:
            response = jsonify(LAST_NAME_EMPTY)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 404

        elif not data["bib_no"]:
            response = jsonify(BIB_NO_EMPTY)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 404

        with engine.connect() as conn:

            query_no_participants = text(
                "SELECT no_of_participants, current_no_of_participants FROM event WHERE id = :id"
            )
            params = dict(id=event_id)

            query_result = conn.execute(query_no_participants, params).fetchone()

            if query_result is None:

                response = jsonify(NO_SINGLE_RUNNER)
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 404

            else:
                no_of_participants, current_no_of_participants = query_result

                if current_no_of_participants <= no_of_participants:

                    query = text(
                        "INSERT INTO runner(event_id,last_name,first_name,bib_no) VALUES (:event_id,:ln, :fn, :bib)"
                    )
                    params = dict(
                        event_id=event_id,
                        ln=data["last_name"],
                        fn=data["first_name"],
                        bib=data["bib_no"],
                    )

                    result = conn.execute(query, params)

                    if result.rowcount > 0:

                        counter += 1

                        update_query = text(
                            "UPDATE event SET current_no_of_participants = :counter WHERE id = :event_id"
                        )
                        conn.execute(update_query, dict(event_id=event_id))
                        conn.commit()

                        response = jsonify(RUNNER_REGISTRATION_SUCCESSFUL)
                        response.headers.add("Access-Control-Allow-Origin", "*")
                        return response, 201

                elif current_no_of_participants > no_of_participants:

                    response = jsonify(MAX_REGISTRATION)
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 200
                else:
                    response = jsonify(RUNNER_REGISTRATION_FAILED)
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 400


# update

# delete
