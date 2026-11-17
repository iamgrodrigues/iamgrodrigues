from pathlib import Path
import re
import xml.etree.ElementTree as ET


def main() -> None:
	readme = Path("README.md")
	content = readme.read_bytes().decode("utf-8")
	start = "<!--START_SECTION:waka-->"
	end = "<!--END_SECTION:waka-->"
	if content.count(start) != 1 or content.count(end) != 1:
		raise ValueError("Expected exactly one WakaTime section in README.md.")
	prefix, section = content.split(start, 1)
	section, suffix = section.split(end, 1)
	assets: dict[Path, str] = {}

	def replace_chart(match: re.Match[str]) -> str:
		svg = match.group()
		if ET.fromstring(svg).tag != "{http://www.w3.org/2000/svg}svg":
			raise ValueError("The generated chart must be a namespaced SVG.")
		number = len(assets) + 1
		path = Path(f"Assets/waka/chart-{number}.svg")
		assets[path] = svg
		image = f"![Development activity chart {number}]({path.as_posix()})"
		fence: tuple[str, str] | None = None
		for marker, language in re.findall(r"^(`{3,}|~{3,})([^\r\n]*)", section[:match.start()], re.MULTILINE):
			if fence is None:
				fence = (marker, language)
			elif marker[0] == fence[0][0] and len(marker) >= len(fence[0]) and not language.strip():
				fence = None
		if fence is not None:
			newline = "\r\n" if "\r\n" in section else "\n"
			marker, language = fence
			return newline.join([marker, "", image, "", marker + language])
		return image

	updated = re.sub(r"<svg\b[^>]*>.*?</svg>", replace_chart, section, flags=re.DOTALL)
	if not assets:
		raise ValueError("No inline SVG charts found in the generated WakaTime section.")
	for path, svg in assets.items():
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(svg + "\n", encoding="utf-8")
	readme.write_bytes((prefix + start + updated + end + suffix).encode("utf-8"))
	print(f"Saved {len(assets)} SVG charts and linked them from README.md.")


if __name__ == "__main__":
	main()
