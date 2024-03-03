# -*- coding: utf-8 -*-
"""
Utility module for django admin classes.
"""

# ======================================================================================================================
# Icons
# ======================================================================================================================

CLOCK_ICON_HTML_RAW_STR = """
<span style="background-image: url('/static/admin/img/icon-clock.svg');
             background-repeat: no-repeat;
             background-position: 0 -16;
             position: relative;
             width: 16px;
             height: 16px;
             display: inline-block;
             vertical-align: middle;
             overflow: hidden;

             filter: {};"
></span>
"""

def get_clock_icon_html(color: str = "black") -> str:
    """Return the HTML for a clock icon."""
    match color:
        case "black":
            return CLOCK_ICON_HTML_RAW_STR.format("invert(0%)")
        case "white":
            return CLOCK_ICON_HTML_RAW_STR.format("invert(100%)")
        case "orange":
            return CLOCK_ICON_HTML_RAW_STR.format(" ".join(("brightness(0)",
                                                            "saturate(100%)",
                                                            "invert(51%)",
                                                            "sepia(49%)",
                                                            "saturate(4518%)",
                                                            "hue-rotate(359deg)",
                                                            "brightness(100%)",
                                                            "contrast(107%)")))
        case _:
            return CLOCK_ICON_HTML_RAW_STR.format("invert(0%)")