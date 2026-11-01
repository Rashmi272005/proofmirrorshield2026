import json
import os
import sqlite3

from datetime import datetime, timezone


def get_connection(database_path):

    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row

    return connection


def init_db(database_path):

    connection = get_connection(database_path)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            input_type TEXT NOT NULL,
            text_preview TEXT,
            url TEXT,
            score INTEGER NOT NULL,
            verdict TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            analysis_json TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_report(database_path, text, url, analysis):

    if text and url:
        input_type = "text_and_url"
    elif text:
        input_type = "text"
    else:
        input_type = "url"

    text_preview = (text or "").strip()[:180]

    connection = get_connection(database_path)

    cursor = connection.execute("""
        INSERT INTO reports (
            created_at, input_type, text_preview,
            url, score, verdict, risk_level, analysis_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).isoformat(),
        input_type,
        text_preview,
        url or "",
        analysis["score"],
        analysis["verdict"],
        analysis["risk_level"],
        json.dumps(analysis)
    ))

    report_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return report_id


def get_report(database_path, report_id):

    connection = get_connection(database_path)

    row = connection.execute(
        "SELECT * FROM reports WHERE id = ?",
        (report_id,)
    ).fetchone()

    connection.close()

    if row is None:
        return None

    result = dict(row)
    result["analysis"] = json.loads(
        result.pop("analysis_json")
    )

    return result


def get_recent_reports(database_path, limit=50):

    connection = get_connection(database_path)

    rows = connection.execute("""
        SELECT id, created_at, input_type, text_preview,
               url, score, verdict, risk_level
        FROM reports
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_dashboard_stats(database_path):

    connection = get_connection(database_path)

    total = connection.execute(
        "SELECT COUNT(*) FROM reports"
    ).fetchone()[0]

    high = connection.execute(
        "SELECT COUNT(*) FROM reports WHERE risk_level = 'high'"
    ).fetchone()[0]

    medium = connection.execute(
        "SELECT COUNT(*) FROM reports WHERE risk_level = 'medium'"
    ).fetchone()[0]

    low = connection.execute(
        "SELECT COUNT(*) FROM reports WHERE risk_level = 'low'"
    ).fetchone()[0]

    connection.close()

    return {
        "total_reports": total,
        "high_risk": high,
        "needs_review": medium,
        "lower_risk": low
    }


# =====================================
# IMAGE DETECTION DATABASE
# =====================================

def init_image_table(database_path):

    connection = get_connection(database_path)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS image_reports (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            created_at TEXT NOT NULL,

            filename TEXT NOT NULL,

            face_detected INTEGER NOT NULL,

            face_count INTEGER NOT NULL,

            image_width INTEGER NOT NULL,

            image_height INTEGER NOT NULL,

            analysis_json TEXT NOT NULL

        )
    """)

    connection.commit()
    connection.close()


def save_image_report(database_path, filename, analysis):

    connection = get_connection(database_path)

    cursor = connection.execute("""
        INSERT INTO image_reports (
            created_at,
            filename,
            face_detected,
            face_count,
            image_width,
            image_height,
            analysis_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).isoformat(),
        filename,
        int(analysis["face_detected"]),
        analysis["face_count"],
        analysis["image_width"],
        analysis["image_height"],
        json.dumps({
            key: value
            for key, value in analysis.items()
            if key != "processed_image"
        })
    ))

    report_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return report_id


def get_image_report(database_path, report_id):

    connection = get_connection(database_path)

    row = connection.execute("""
        SELECT *
        FROM image_reports
        WHERE id = ?
    """, (report_id,)).fetchone()

    connection.close()

    if row is None:
        return None

    result = dict(row)

    result["analysis"] = json.loads(
        result.pop("analysis_json")
    )

    return result


def get_image_history(database_path):

    connection = get_connection(database_path)

    rows = connection.execute("""
        SELECT id, created_at, filename,
               face_detected, face_count,
               image_width, image_height
        FROM image_reports
        ORDER BY id DESC
        LIMIT 30
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]