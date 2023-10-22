"""Server implementation for Recommendations microservice.
"""

import grpc
from random import sample as choose
from concurrent.futures import ThreadPoolExecutor

from recommendations_pb2 import (
    BookCategory,
    BookRecommendation,
    BookRecommendationResponse,
)
import recommendations_pb2_grpc

MAX_THREADS = 10  # overkill, but standard
PORT = 50051  # default gRPC port

books_by_category = {
    BookCategory.MYSTERY: [
        BookRecommendation(bookID=1, title="The Maltese Falcon"),
        BookRecommendation(bookID=2, title="Murder on the Orient Express"),
        BookRecommendation(bookID=3, title="The Hound of the Baskervilles"),
    ],
    BookCategory.SCIENCE_FICTION: [
        BookRecommendation(bookID=4,
                           title="The Hitchhiker's Guide to the Galaxy"),
        BookRecommendation(bookID=5, title="Ender's Game"),
        BookRecommendation(bookID=6, title="The Dune Chronicles"),
    ],
    BookCategory.SELF_HELP: [
        BookRecommendation(bookID=7,
                           title="The 7 Habits of Highly Effective People"),
        BookRecommendation(bookID=8,
                           title="How to Win Friends and Influence People"),
        BookRecommendation(bookID=9, title="Man's Search for Meaning"),
    ],
}


class BookRecommendationService(
        recommendations_pb2_grpc.BookRecommendationServiceServicer):

    def RecommendBooks(self, request, context):
        if request.category not in books_by_category:
            # We avoid raising an exception in order to ensure the correct status is returned
            # Alternatively, we could use the protobuf "Interceptor" pattern to catch the
            # exception and set the status accordingly
            context.abort(grpc.StatusCode.NOT_FOUND,
                          f"Category {request.category} not found")
        choices = books_by_category[request.category]
        num_books = min(len(choices), request.maxResults)
        books = choose(choices, num_books)

        return BookRecommendationResponse(recommendations=books)


def serve():
    server = grpc.server(ThreadPoolExecutor(max_workers=MAX_THREADS))
    recommendations_pb2_grpc.add_BookRecommendationServiceServicer_to_server(
        BookRecommendationService(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
