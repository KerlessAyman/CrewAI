from Report_Writer import *
def preview_report(report_md, max_lines=20):
    lines = report_md.split('\n')
    preview_lines = lines[:max_lines]
    print("\n".join(preview_lines))
    if len(lines) > max_lines:
        print("\n... (Report truncated for preview) ...\n")
if __name__ == "__main__":

    preview_report(report_md, max_lines=30)
