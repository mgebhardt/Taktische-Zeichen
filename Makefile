
.SECONDEXPANSION:

# Alle Jinja2 Templates im Ordner symbols finden
YML_SOURCES = $(shell find symbols/ -name *.yml)
SVG_SOURCES = $(shell find build/svg -name *.svg)

# symbols/ prefix entfernen für die Ausgabedateien
SVG_TARGET_PATHS = $(YML_SOURCES:symbols/%=%)
PNG_TARGET_PATHS = $(SVG_SOURCES:build/svg/%=%)

# Zieldateien für SVG und PNG Ausgabe festlegen
SVG_TARGETS = $(SVG_TARGET_PATHS:.yml=.svg)
PNG_TARGETS = $(PNG_TARGET_PATHS:.svg=.png)

SVG_FILES = $(addprefix build/svg/,$(SVG_TARGETS))
PNG_1024_FILES = $(addprefix build/png/1024/,$(PNG_TARGETS))
PNG_512_FILES = $(addprefix build/png/512/,$(PNG_TARGETS))
PNG_256_FILES = $(addprefix build/png/256/,$(PNG_TARGETS))

# Erstellt alle SVG Ausgabedateien
svg: $(SVG_FILES)

build/svg/%.svg: symbols/%.yml
	mkdir -p $(@D)
	./scripts/j2build.py ./templates/ $< $@

# Erstellt alle PNG Ausgabedateien
png: $$(PNG_1024_FILES) $$(PNG_512_FILES) $$(PNG_256_FILES)

build/png/1024/%.png: build/svg/%.svg
	mkdir -p $(@D)
	phantomjs rasterize.js $^ $@ 1024px*1024px 4
	optipng -quiet $@

build/png/512/%.png: build/svg/%.svg
	mkdir -p $(@D)
	phantomjs rasterize.js $^ $@ 512px*512px 2
	optipng -quiet $@

build/png/256/%.png: build/svg/%.svg
	mkdir -p $(@D)
	phantomjs rasterize.js $^ $@ 256px*256px 1
	optipng -quiet $@

clean:
	rm -rf build
	rm Taktische-Zeichen.zip

all: svg png

release: all
	cd build && zip -r ../Taktische-Zeichen.zip ./*

ci: all
	cd build && zip -r ../release.zip ./*

web: all
	mkdir -p ./web/build
	cp -r ./build/ ./web/
	find build/ -name *.svg > ./web/symbols.lst
