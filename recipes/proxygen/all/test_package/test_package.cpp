#include <proxygen/httpserver/HTTPServer.h>
#include <proxygen/httpserver/RequestHandlerFactory.h>

int main() {

    proxygen::HTTPServerOptions options;
    proxygen::HTTPServer server(std::move(options));

    // server.bind(IPs);
    // std::jthread t([&]() { server.start(); });

    return EXIT_SUCCESS;
}
