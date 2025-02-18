# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from fasthtml import svg


def github_logo() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d=(
                "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205"
                " 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04"
                "-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7"
                " 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838"
                " 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108"
                "-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93"
                " 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176"
                " 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405"
                " 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285"
                "-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23"
                " 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81"
                " 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825"
                ".57C20.565 22.092 24 17.592 24 12.297c0-6.627"
                "-5.373-12-12-12"
            ),
        ),
        width="24",
        height="24",
        viewBox="0 0 24 24",
        fill="currentColor",
        cls="hover:animate-spin",
    )


def home() -> svg.Svg:
    return svg.Svg(
        svg.Path(d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"),
        svg.Path(
            d=(
                "M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7"
                " 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
            )
        ),
        width="24",
        height="24",
        viewbox="0 0 24 24",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
        cls=(
            "dark:hover:stroke-neutral-100",
            "dark:stroke-blue-500",
            "fill-none",
            "hover:stroke-blue-900",
            "stroke-neutral-200",
        ),
    )


def badge_document() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def badge_experimental() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2",
        ),
        svg.Path(
            d="M8.5 2h7",
        ),
        svg.Path(
            d="M7 16h10",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def badge_stable() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",
        ),
        svg.Path(
            d="m9 12 2 2 4-4",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def file_stack() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M21 7h-3a2 2 0 0 1-2-2V2",
        ),
        svg.Path(
            d="M21 6v6.5c0 .8-.7 1.5-1.5 1.5h-7c-.8 0-1.5-.7-1.5-1.5v-9c0-.8.7-1.5 1.5-1.5H17Z",
        ),
        svg.Path(
            d="M7 8v8.8c0 .3.2.6.4.8.2.2.5.4.8.4H15",
        ),
        svg.Path(
            d="M3 12v8.8c0 .3.2.6.4.8.2.2.5.4.8.4H11",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def lock_icon(state: t.Literal["open", "closed"]) -> svg.Svg:
    if state == "open":
        d = (
            "M13.5 10.5V6.75a4.5 4.5 0 1 1 9 0v3.75M3.75 21.75h10.5a2.25 2.25"
            " 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H3.75a2.25 2.25"
            " 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"
        )
    else:
        d = (
            "M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75"
            " 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25"
            " 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25"
            " 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"
        )
    return svg.Svg(
        svg.Path(
            d=d,
            clip_rule="evenodd",
            stroke_linecap="round",
            stroke_linejoin="round",
        ),
        viewbox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        cls="size-6 flex-none text-gray-400 stroke-2",
    )


def dark_theme() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z",
        ),
        width="24",
        height="24",
        viewBox="0 0 24 24",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
        cls="stroke-blue-500 fill-none",
    )


def light_theme() -> svg.Svg:
    return svg.Svg(
        svg.Circle(cx="12", cy="12", r="4"),
        svg.Path(d="M12 2v2"),
        svg.Path(d="M12 20v2"),
        svg.Path(d="m4.93 4.93 1.41 1.41"),
        svg.Path(d="m17.66 17.66 1.41 1.41"),
        svg.Path(d="M2 12h2"),
        svg.Path(d="M20 12h2"),
        svg.Path(d="m6.34 17.66-1.41 1.41"),
        svg.Path(d="m19.07 4.93-1.41 1.41"),
        width="24",
        height="24",
        viewBox="0 0 24 24",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
        cls="stroke-blue-500 fill-none",
    )


def magnifying_glass() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            fill_rule="evenodd",
            d=(
                "M9 3.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11ZM2 9a7"
                " 7 0 1 1 12.452 4.391l3.328 3.329a.75.75 0 1 1-1.06"
                " 1.06l-3.329-3.328A7 7 0 0 1 2 9Z"
            ),
            clip_rule="evenodd",
        ),
        viewBox="0 0 20 20",
        fill="currentColor",
        aria_hidden="true",
        data_slot="icon",
        cls=(
            "pointer-events-none col-start-1 row-start-1 ml-3 size-5"
            " self-center text-gray-400"
        ),
    )


def printer() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2",
        ),
        svg.Path(
            d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6",
        ),
        svg.Rect(x="6", y="14", width="12", height="8", rx="1"),
        width="24",
        height="24",
        viewBox="0 0 24 24",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
        cls=(
            "dark:hover:stroke-neutral-100",
            "dark:stroke-blue-500",
            "fill-none",
            "hover:stroke-blue-900",
            "stroke-neutral-200",
        ),
    )


def report() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z",
        ),
        svg.Path(
            d="M14 2v4a2 2 0 0 0 2 2h4",
        ),
        svg.Path(
            d="M10 9H8",
        ),
        svg.Path(
            d="M16 13H8",
        ),
        svg.Path(
            d="M16 17H8",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def spinner(scale: float) -> svg.Svg:
    size = int(scale * 5)
    return svg.Svg(
        svg.Circle(
            cx="12",
            cy="12",
            r="10",
            stroke_width="4",
            cls="opacity-25",
        ),
        svg.Path(
            d=(
                "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2"
                " 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3"
                " 7.938l3-2.647z"
            ),
            cls=("opacity-75", "fill-blue-500"),
        ),
        xmlns="http://www.w3.org/2000/svg",
        fill="none",
        viewbox="0 0 24 24",
        cls=(
            "mr-3",
            "-ml-1",
            "animate-spin",
            "stroke-blue-500",
            f"h-{size} w-{size}",
        ),
    )
