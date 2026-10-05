import { Fragment, type ReactNode } from "react";

// Tiny, safe Markdown renderer for chat bubbles: **bold**, line breaks, and -/* bullet lists.
// Builds React elements directly (no dangerouslySetInnerHTML), so nothing is injected as HTML.

function renderInline(text: string, keyPrefix: string): ReactNode[] {
  // Split on **bold** spans.
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (/^\*\*[^*]+\*\*$/.test(part)) {
      return <strong key={`${keyPrefix}-b${i}`}>{part.slice(2, -2)}</strong>;
    }
    return <Fragment key={`${keyPrefix}-t${i}`}>{part}</Fragment>;
  });
}

export default function Markdown({ text }: { text: string }) {
  const lines = text.split("\n");
  const blocks: ReactNode[] = [];
  let bullets: string[] = [];

  const flushBullets = () => {
    if (bullets.length) {
      blocks.push(
        <ul key={`ul-${blocks.length}`} className="md-list">
          {bullets.map((b, i) => (
            <li key={i}>{renderInline(b, `li-${blocks.length}-${i}`)}</li>
          ))}
        </ul>
      );
      bullets = [];
    }
  };

  lines.forEach((line, i) => {
    const bullet = line.match(/^\s*[-*]\s+(.*)$/);
    if (bullet) {
      bullets.push(bullet[1]);
      return;
    }
    flushBullets();
    if (line.trim() === "") return;
    blocks.push(
      <p key={`p-${i}`} className="md-p">
        {renderInline(line, `p-${i}`)}
      </p>
    );
  });
  flushBullets();

  return <>{blocks}</>;
}
