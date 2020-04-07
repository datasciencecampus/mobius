# -*- coding: utf-8 -*-
"""Extract text data from the Mobility PDF.

Coordinates are taken from the bottom left of each page (72 dpi).

To find plots we use the 'Baseline' y-axis label.

The following are hard coded:

* Location of country name
* location of category (relative to 'Baseline' anchor)
* location of headline trend (relative to 'Baseline' anchor)
* location of region name (relative to 'Baseline' anchor of top left plot)

Usage:
    Main entry point is `summarise`, this turn the PDF into a DataFrame of
    the headline figures.
"""
import collections

import pandas as pd
import rtree

Anchor = collections.namedtuple("Anchor", ["left", "bottom"])

PlotElements = collections.namedtuple("PlotElements", ["anchor", "plot_name", "headline_figure"])


class PageData:
    __COUNTRY_NAME_FIXED_BOX = (20, 740, 580, 780)
    __HEADING_DATE_STRING = "March 29, 2020"

    __COUNTRY_HEADLINE_OFFSETS = (-130, -20, -20, 40)
    __COUNTRY_PLOT_NAME_OFFSETS = (- 130, 40, -20, 60)

    __HEADLINE_OFFSETS = (-10, 45, 140, 65)
    __PLOT_NAME_OFFSETS = (-5, 70, 100, 90)

    __REGION_OFFSETS = (-20, 100, 500, 140)

    __COUNTRY_PAGES = {1, 2}

    def __init__(self, page_num, text_elements):
        self.page_num = page_num
        self.bbox_to_text, self.text_to_corner = PageData.index(text_elements)

    def __getitem__(self, item):
        return self.text_to_corner[item]

    def intersecting_boxes(self, bbox):
        return list(self.bbox_to_text.intersection(bbox, objects=True))

    def text_in_box(self, bbox):
        boxes = self.intersecting_boxes(bbox)

        return "".join(box.object for box in boxes)

    def country_name(self):
        if self.page_num != 1:
            raise ValueError("country_name only present on first page")

        text = self.text_in_box(PageData.__COUNTRY_NAME_FIXED_BOX)
        return text.replace(PageData.__HEADING_DATE_STRING, "").strip()

    def headline_figure(self, anchor):

        if self.page_num in PageData.__COUNTRY_PAGES:
            offset = PageData.__COUNTRY_HEADLINE_OFFSETS
        else:
            offset = PageData.__HEADLINE_OFFSETS

        bbox = PageData.__apply_offset(anchor, offset)

        boxes = self.intersecting_boxes(bbox)

        return boxes[0].object.replace("*\n", "").replace("compared to baseline", "").strip()

    def plot_name(self, anchor):

        if self.page_num in PageData.__COUNTRY_PAGES:
            offset = PageData.__COUNTRY_PLOT_NAME_OFFSETS
        else:
            offset = PageData.__PLOT_NAME_OFFSETS

        bbox = PageData.__apply_offset(anchor, offset)
        boxes = sorted(self.intersecting_boxes(bbox), key=lambda item: item.bbox)

        plot_names = [text.object for text in boxes]

        clean_names = [name for name in plot_names if "baseline" not in name]
        asterisks = ["*" for name in plot_names if "baseline" in name]

        plot_name = "".join(clean_names + asterisks)

        return plot_name

    def region(self, anchor):
        bbox = self.__apply_offset(anchor, PageData.__REGION_OFFSETS)

        text = self.text_in_box(bbox)
        return text

    @staticmethod
    def __apply_offset(anchor: Anchor, offset):
        return (
            anchor.left + offset[0],
            anchor.bottom + offset[1],
            anchor.left + offset[2],
            anchor.bottom + offset[3]
        )

    @staticmethod
    def index(text_elements):
        bbox_to_text = rtree.Rtree()
        text_to_corner = collections.defaultdict(list)

        for idx, (bbox, text) in enumerate(text_elements):
            bbox_to_text.add(idx, bbox, text.strip())
            text_to_corner[text.replace("*", "").strip()].append(Anchor(bbox[0], bbox[1]))

        return bbox_to_text, text_to_corner


def _country_level_extractor(page_data: PageData):

    anchors = page_data["Baseline"]

    elements = []

    for anchor in anchors:

        headline_figure = page_data.headline_figure(anchor)

        plot_name = page_data.plot_name(anchor)

        elements.append(PlotElements(anchor, plot_name, headline_figure))

    return [("__ALL", sort_elements(elements))]


EXTRACTORS = dict.fromkeys([1, 2], _country_level_extractor)


def region_level_extractor(page_data: PageData):

    anchors = page_data["Baseline"]

    top_region = "top_region"
    bottom_region = "bottom_region"

    elements = {top_region: list(), bottom_region: list()}

    if len(anchors) == 0:
        return list()

    top_anchors = []
    bottom_anchors = []

    for anchor in anchors:

        if anchor.bottom > 500:
            region_key = top_region
            top_anchors.append(anchor)
        else:
            region_key = bottom_region
            bottom_anchors.append(anchor)

        headline_figure = page_data.headline_figure(anchor)

        plot_name = page_data.plot_name(anchor)

        elements[region_key].append(PlotElements(anchor, plot_name, headline_figure))

    result = []

    top_plots = sort_elements(elements["top_region"])
    _process_plots(top_plots, page_data, result)

    bottom_plots = sort_elements(elements["bottom_region"])
    _process_plots(bottom_plots, page_data, result)

    return result


def _process_plots(plots, page_data, result):
    if plots:
        region_anchor = plots[0].anchor
        region = page_data.region(region_anchor)

        result.append((region, plots))


def sort_elements(elements):

    elements = sorted(elements, key=lambda row: int(round(row.anchor.left, -1)))
    elements = sorted(elements, key=lambda row: int(round(row.anchor.bottom, -1)), reverse=True)

    return elements


def page_gen(filepath):
    import pdfminer.converter
    import pdfminer.layout
    import pdfminer.pdfinterp
    import pdfminer.pdfpage

    document = open(filepath, 'rb')
    rsrcmgr = pdfminer.pdfinterp.PDFResourceManager()
    laparams = pdfminer.layout.LAParams(all_texts=True)
    device = pdfminer.converter.PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = pdfminer.pdfinterp.PDFPageInterpreter(rsrcmgr, device)

    for page_num, page in enumerate(pdfminer.pdfpage.PDFPage.get_pages(document), start=1):

        interpreter.process_page(page)
        layout = device.get_result()

        yield text_gen(layout)


def text_gen(layout):
    import pdfminer.layout

    for element in layout:
        if isinstance(element, pdfminer.layout.LTTextBoxHorizontal):
            yield element.bbox, element.get_text()


def _extract(filepath):

    country = None

    for page_num, text_elements in enumerate(page_gen(filepath), start=1):

        page_data = PageData(page_num, text_elements)

        if page_num == 1:
            country = page_data.country_name()

        extractor = EXTRACTORS.get(page_num, region_level_extractor)

        data = extractor(page_data)

        for region, plots in data:
            if region == "__ALL":
                region = country

            for plot in plots:

                yield country, region, page_num, plot


def summarise(filepath):
    print(f"Creating summary data for {filepath}")

    results = []
    for idx, data in enumerate(_extract(filepath), start=1):

        if idx % 6 == 0 and idx > 0:
            print(f"Processed {idx} summary plots")

        country, region, page_num, plot_elements = data

        row_dict = {
            "country": country,
            "region": region,
            "page_num": page_num,
            "plot_num": idx,
            "plot_name": plot_elements.plot_name,
            "headline": plot_elements.headline_figure
        }
        results.append(row_dict)

    df = pd.DataFrame(results)
    df["asterisk"] = df.plot_name.str.contains("*", regex=False)
    df.plot_name = df.plot_name.str.replace(pat="*", repl="", regex=False)

    return df[["country", "page_num", "plot_num", "region", "plot_name", "asterisk", "headline"]]
