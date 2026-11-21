"use client";

import { useEffect, useId, useRef, useState, type FocusEvent, type KeyboardEvent } from "react";

export type ThemeSelectOption = { value: string; label: string };

type ThemeSelectProps = {
  id?: string;
  name?: string;
  label?: string;
  options: ThemeSelectOption[];
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
};

export function ThemeSelect({ id, name, label, options, value, defaultValue = "", onChange }: ThemeSelectProps) {
  const autoId = useId();
  const buttonId = id ?? `${autoId}-button`;
  const labelId = `${autoId}-label`;
  const valueId = `${autoId}-value`;
  const listId = `${autoId}-list`;
  const rootRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const selectRef = useRef<HTMLSelectElement>(null);
  const typeBuffer = useRef("");
  const typeTimer = useRef<number | undefined>(undefined);
  const [open, setOpen] = useState(false);
  const [uncontrolled, setUncontrolled] = useState(defaultValue);
  const [activeIndex, setActiveIndex] = useState(0);
  const [up, setUp] = useState(false);
  const current = value ?? uncontrolled;
  const selectedIndex = Math.max(
    0,
    options.findIndex((option) => option.value === current),
  );
  const selected = options[selectedIndex];

  useEffect(() => {
    const select = selectRef.current;
    if (!select) return;
    select.tabIndex = -1;
    select.setAttribute("aria-hidden", "true");
  }, []);

  useEffect(() => {
    if (!open) return;
    const root = rootRef.current;
    if (root) {
      const rect = root.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      const spaceAbove = rect.top;
      setUp(spaceBelow < 360 && spaceAbove > spaceBelow);
    }
    listRef.current?.focus({ preventScroll: true });
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const list = listRef.current;
    const option = list?.querySelector<HTMLElement>("[data-active='true']");
    if (!list || !option) return;
    const top = option.offsetTop;
    const bottom = top + option.offsetHeight;
    if (top < list.scrollTop) list.scrollTop = top;
    else if (bottom > list.scrollTop + list.clientHeight) list.scrollTop = bottom - list.clientHeight;
  }, [open, activeIndex]);

  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: PointerEvent) {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  function commit(next: string) {
    if (selectRef.current) selectRef.current.value = next;
    if (value === undefined) setUncontrolled(next);
    onChange?.(next);
    setOpen(false);
    buttonRef.current?.focus({ preventScroll: true });
  }

  function openAt(index: number) {
    setActiveIndex(index);
    setOpen(true);
  }

  function move(delta: number) {
    if (options.length === 0) return;
    setActiveIndex((index) => (index + delta + options.length) % options.length);
  }

  function onButtonKey(event: KeyboardEvent<HTMLButtonElement>) {
    if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openAt(selectedIndex);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      openAt(Math.max(0, selectedIndex));
    }
  }

  function onListKey(event: KeyboardEvent<HTMLUListElement>) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      move(1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      move(-1);
    } else if (event.key === "Home") {
      event.preventDefault();
      setActiveIndex(0);
    } else if (event.key === "End") {
      event.preventDefault();
      setActiveIndex(Math.max(0, options.length - 1));
    } else if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      const option = options[activeIndex];
      if (option) commit(option.value);
    } else if (event.key === "Escape") {
      event.preventDefault();
      setOpen(false);
      buttonRef.current?.focus({ preventScroll: true });
    } else if (event.key === "Tab") {
      setOpen(false);
    } else if (event.key.length === 1 && !event.altKey && !event.ctrlKey && !event.metaKey) {
      typeBuffer.current = `${typeBuffer.current}${event.key}`.toLowerCase();
      window.clearTimeout(typeTimer.current);
      typeTimer.current = window.setTimeout(() => {
        typeBuffer.current = "";
      }, 500);
      const query = typeBuffer.current;
      const start = (activeIndex + 1) % Math.max(options.length, 1);
      const ordered = [...options.slice(start), ...options.slice(0, start)];
      const found = ordered.findIndex((option) => option.label.toLowerCase().startsWith(query));
      if (found >= 0) setActiveIndex((start + found) % options.length);
    }
  }

  return (
    <div
      className="theme-select"
      ref={rootRef}
      onBlur={(event: FocusEvent<HTMLDivElement>) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
      }}
    >
      {label ? (
        <label className="theme-select-label" id={labelId} htmlFor={buttonId}>
          {label}
        </label>
      ) : null}
      <div className="theme-select-box">
        <select
          ref={selectRef}
          className="select-field theme-select-native"
          name={name}
          aria-labelledby={label ? labelId : undefined}
          {...(value === undefined ? { defaultValue } : { value })}
          onChange={(event) => {
            if (value === undefined) setUncontrolled(event.target.value);
            onChange?.(event.target.value);
          }}
        >
          {options.map((option, index) => (
            <option key={`${option.value}-${index}`} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <div className="theme-select-ui">
          <button
            ref={buttonRef}
            type="button"
            id={buttonId}
            className="theme-select-button"
            aria-haspopup="listbox"
            aria-expanded={open}
            aria-controls={listId}
            aria-labelledby={label ? `${labelId} ${valueId}` : undefined}
            onClick={() => (open ? setOpen(false) : openAt(selectedIndex))}
            onKeyDown={onButtonKey}
          >
            <span id={valueId}>{selected?.label}</span>
            <svg className="theme-select-chevron" viewBox="0 0 12 8" width="12" height="8" aria-hidden="true">
              <path d="M1 1.5 6 6.5 11 1.5" fill="none" stroke="currentColor" strokeWidth="1.4" />
            </svg>
          </button>
          <ul
            id={listId}
            ref={listRef}
            role="listbox"
            hidden={!open}
            tabIndex={-1}
            aria-labelledby={label ? labelId : undefined}
            aria-activedescendant={open ? `${listId}-opt-${activeIndex}` : undefined}
            className={up ? "theme-select-list is-up" : "theme-select-list"}
            onKeyDown={onListKey}
          >
            {options.map((option, index) => (
              <li
                key={`${option.value}-${index}`}
                id={`${listId}-opt-${index}`}
                role="option"
                aria-selected={option.value === current}
                data-active={index === activeIndex ? "true" : "false"}
                className={index === activeIndex ? "theme-select-option is-active" : "theme-select-option"}
                onMouseEnter={() => setActiveIndex(index)}
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => commit(option.value)}
              >
                {option.label}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
