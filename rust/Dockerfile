FROM rust:1-buster as build

# create a new empty shell project
RUN USER=root cargo new --bin app
WORKDIR /app

# copy over your manifests
COPY ./Cargo.lock ./Cargo.lock
COPY ./Cargo.toml ./Cargo.toml

# this build step will cache your dependencies
RUN cargo build --release
RUN rm src/*.rs

# copy your source tree
COPY ./src ./src
COPY ./.sqlx ./.sqlx

# build for release
RUN rm ./target/release/deps/speedtests_rs*
RUN cargo build --release

FROM debian:buster-slim
ARG APP=/usr/src/app

EXPOSE 3000

ENV TZ=Etc/UTC \
    APP_USER=appuser

RUN groupadd $APP_USER \
    && useradd -g $APP_USER $APP_USER \
    && mkdir -p ${APP}

COPY --from=build /app/target/release/speedtests-rs ${APP}/speedtests-rs

COPY ./templates ${APP}/templates

RUN chown -R $APP_USER:$APP_USER ${APP}

USER $APP_USER
WORKDIR ${APP}

CMD ["./speedtests-rs"]
