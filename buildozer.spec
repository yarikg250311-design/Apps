[app]
title = PC Parts Finder
package.name = pcpartsfinder
package.domain = org.pcparts

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,svg

version = 0.1

requirements = python3,kivy,kivymd,requests,beautifulsoup4,certifi,urllib3,idna,charset-normalizer,pygments,materialyoucolor

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/assets/icons/app_icon.png

android.permissions = INTERNET

android.api = 34
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
