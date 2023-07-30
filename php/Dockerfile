FROM php:8.2-fpm-alpine


ENV MUSL_LOCPATH /usr/share/i18n/locales/musl

# This is grabbed from an internal configuration, PHP was the benchmark so hence this was kept the same.

RUN apk add --no-cache musl-locales musl-locales-lang icu-data-full \
    && apk add --no-cache --virtual .phpize-deps $PHPIZE_DEPS freetype-dev libpng-dev libjpeg-turbo-dev libwebp-dev libxml2-dev zlib-dev icu-dev imagemagick-dev gettext-dev libtool \
    && export CFLAGS="$PHP_CFLAGS" CPPFLAGS="$PHP_CPPFLAGS" LDFLAGS="$PHP_LDFLAGS" \
    && docker-php-ext-configure gd \
        --with-freetype\
        --with-webp \
        --with-jpeg \   
    && docker-php-ext-install -j$(nproc) gd \
    && docker-php-ext-configure intl \
    && docker-php-ext-install -j$(nproc) intl \
    && docker-php-ext-install -j$(nproc) mysqli \
    #&& docker-php-ext-install pgsql \
    && docker-php-ext-install -j$(nproc) gettext \
    && docker-php-ext-install -j$(nproc) opcache \
    #&& docker-php-ext-install soap \
    && pecl install imagick \
    && docker-php-ext-enable imagick \
    && pecl install redis \
    && docker-php-ext-enable redis \
    && apk --update add --no-cache --virtual .imagick-runtine-deps imagemagick libgomp \
    && apk --update add --no-cache --virtual .intl-runtine-deps icu-libs \
    && apk --update add --no-cache --virtual .gettext-runtine-deps gettext-libs \
    && apk del .phpize-deps \
    && rm -vrf /tmp/* /var/cache/apk/* /usr/src/* \
    && cd "${MUSL_LOCPATH}" \
    && for i in *.UTF-8; do cp -a "$i" "${i%%UTF-8}"; done \
    && ls -lah

WORKDIR /var/www/html

ENV LANG=en_US \
    LANGUAGE=en_US

COPY ./php.ini /usr/local/etc/php
    
COPY . /var/www/html