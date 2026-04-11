import epubGen from 'epub-gen-memory';
import fs from 'fs/promises';

const epub = (epubGen as any).default || epubGen;

async function test() {
  const buffer = await epub({
    title: "Test Book",
    author: "Test Author"
  }, [{ title: "Chapter 1", content: "<p>Hello World</p>" }]);
  await fs.writeFile("test.epub", buffer);
  console.log("Success");
}

test().catch(console.error);
