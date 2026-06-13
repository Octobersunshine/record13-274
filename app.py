import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/bar_chart", methods=["POST"])
def bar_chart():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    categories = data.get("categories")
    values = data.get("values")
    colors = data.get("colors")
    title = data.get("title", "Bar Chart")
    xlabel = data.get("xlabel", "Categories")
    ylabel = data.get("ylabel", "Values")

    if not categories or not values:
        return jsonify({"error": "Both 'categories' and 'values' are required"}), 400
    if len(categories) != len(values):
        return jsonify({"error": "'categories' and 'values' must have the same length"}), 400
    if colors is not None and not isinstance(colors, list):
        return jsonify({"error": "'colors' must be a list of color strings"}), 400
    if colors and len(colors) != len(categories):
        return jsonify({"error": "'colors' must have the same length as 'categories'"}), 400

    MAX_BARS = 10
    truncated = False

    if colors:
        paired = list(zip(categories, values, colors))
        paired.sort(key=lambda x: x[1], reverse=True)
    else:
        paired = list(zip(categories, values))
        paired.sort(key=lambda x: x[1], reverse=True)

    if len(paired) > MAX_BARS:
        if colors:
            top = paired[: MAX_BARS - 1]
            others_sum = sum(v for _, v, _ in paired[MAX_BARS - 1 :])
            top.append(("其他", others_sum, "#888888"))
            paired = top
        else:
            top = paired[: MAX_BARS - 1]
            others_sum = sum(v for _, v in paired[MAX_BARS - 1 :])
            top.append(("其他", others_sum))
            paired = top
        truncated = True

    display_categories = []
    display_values = []
    display_colors = []
    for item in paired:
        display_categories.append(item[0])
        display_values.append(item[1])
        if colors:
            display_colors.append(item[2])

    bar_color = display_colors if colors else "steelblue"

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(display_categories, display_values, color=bar_color, edgecolor="white")

    for bar, val in zip(bars, display_values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(val),
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)

    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    return jsonify({"image_base64": img_b64, "truncated": truncated})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
