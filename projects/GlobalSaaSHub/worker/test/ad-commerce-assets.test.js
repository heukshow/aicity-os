// In-memory actual PNG fixtures only. No external services or filesystem writes.
import test from 'node:test';
import assert from 'node:assert/strict';
import { deflateSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import { validateAdAsset, AD_ASSET_MIME_TYPES } from '../src/ad-commerce-assets.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';

function crc32(bytes) {
  let value = 0xffffffff;
  for (const byte of bytes) {
    value ^= byte;
    for (let bit = 0; bit < 8; bit++) value = value & 1 ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
  }
  return (value ^ 0xffffffff) >>> 0;
}
function chunk(type, data = Buffer.alloc(0)) {
  const result = Buffer.alloc(data.length + 12);
  result.writeUInt32BE(data.length); result.write(type, 4, 'ascii'); data.copy(result, 8);
  result.writeUInt32BE(crc32(result.subarray(4, -4)), result.length - 4);
  return result;
}
function png({ width = 400, height = 400, color = 6, depth = 8, interlace = 0,
  scanlines, imageData, before = [], after = [], split = false } = {}) {
  const header = Buffer.alloc(13);
  header.writeUInt32BE(width); header.writeUInt32BE(height, 4);
  header[8] = depth; header[9] = color; header[12] = interlace;
  const channels = { 0: 1, 2: 3, 4: 2, 6: 4 }[color] || 4;
  const raw = scanlines || Buffer.alloc((width * channels + 1) * height);
  const compressed = imageData || deflateSync(raw);
  const image = split ? [chunk('IDAT', compressed.subarray(0, 3)), chunk('IDAT', compressed.subarray(3))]
    : [chunk('IDAT', compressed)];
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk('IHDR', header), ...before, ...image, ...after, chunk('IEND')]);
}
const valid = png();

test('all nine asset roles accept bounded, actual PNGs with exact dimensions and content hashes', async () => {
  assert.deepEqual(AD_ASSET_MIME_TYPES, ['image/png']);
  for (const [role, spec] of Object.entries(AD_ASSET_SPECS)) {
    const source = png({ width: spec.width, height: spec.height, split: true });
    const result = await validateAdAsset(role, 'image/png', source);
    assert.equal(result.mime, 'image/png'); assert.equal(result.width, spec.width);
    assert.equal(result.height, spec.height); assert.equal(result.byte_size, source.length);
    assert.equal(result.sha256, createHash('sha256').update(source).digest('hex'));
    assert.ok(result.data instanceof Uint8Array);
    assert.deepEqual(Buffer.from(result.data), source);
  }
});
test('supported grayscale/RGB/grayscale-alpha/RGBA channel counts are decoded', async () => {
  for (const color of [0, 2, 4, 6]) await validateAdAsset('tool-primary', 'image/png', png({ color, width: 600, height: 600 }));
});
test('caller mutation cannot change validated bytes or hash', async () => {
  const source = Buffer.from(valid);
  const pending = validateAdAsset('logo', 'image/png', source);
  source.fill(0);
  const result = await pending;
  assert.deepEqual(Buffer.from(result.data), valid);
  assert.equal(result.sha256, createHash('sha256').update(valid).digest('hex'));
});
test('unsupported role including object prototype names is rejected', async () => {
  for (const role of ['unknown', 'toString', '__proto__']) {
    await assert.rejects(validateAdAsset(role, 'image/png', valid), /unsupported role/);
  }
});
test('JPEG, WebP and ambiguous MIME declarations are explicitly unsupported', async () => {
  for (const mime of ['image/jpeg', 'image/webp', 'text/plain', 'image/png; charset=UTF-8']) {
    await assert.rejects(validateAdAsset('logo', mime, valid), /unsupported MIME/);
  }
});
test('declared PNG must have the actual PNG signature', async () => {
  const source = Buffer.from(valid); source[0] = 0xff;
  await assert.rejects(validateAdAsset('logo', 'image/png', source), /signature/);
});
test('exact role dimensions are enforced', async () => {
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ width: 399 })), /dimensions/);
});
test('files exceeding the role limit are rejected before parsing', async () => {
  await assert.rejects(validateAdAsset('logo', 'image/png', new Uint8Array(100001)), /size limit/);
});
test('missing bytes, truncated chunks and dishonest chunk lengths are rejected', async () => {
  for (const source of [new Uint8Array(1), valid.subarray(0, 20), valid.subarray(0, -5)]) {
    await assert.rejects(validateAdAsset('logo', 'image/png', source), /truncated|bounds/);
  }
  const source = Buffer.from(valid); source.writeUInt32BE(0xffffffff, 8);
  await assert.rejects(validateAdAsset('logo', 'image/png', source), /bounds/);
});
test('invalid byte input is rejected', async () => {
  for (const source of [null, 'not an image', [137, 80]]) {
    await assert.rejects(validateAdAsset('logo', 'image/png', source), /byte input/);
  }
});
test('CRC mismatch is rejected even with a valid DEFLATE stream', async () => {
  const source = Buffer.from(valid); source[29] ^= 1;
  await assert.rejects(validateAdAsset('logo', 'image/png', source), /CRC/);
});
test('CRC-correct but invalid DEFLATE bytes are rejected', async () => {
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ imageData: Buffer.from('not-deflate') })), /image data/);
});
test('CRC-correct but incorrect Adler checksum is rejected', async () => {
  const imageData = deflateSync(Buffer.alloc(1601 * 400)); imageData[imageData.length - 1] ^= 1;
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ imageData })), /image data/);
});
test('too few or too many decoded scanline bytes are rejected with bounded output', async () => {
  for (const length of [1601 * 400 - 1, 1601 * 400 + 1, 1601 * 400 * 20]) {
    await assert.rejects(validateAdAsset('logo', 'image/png', png({ scanlines: Buffer.alloc(length) })), /size/);
  }
});
test('invalid scanline filter is rejected, including on a later row', async () => {
  const scanlines = Buffer.alloc(1601 * 400); scanlines[1601 * 37] = 5;
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ scanlines })), /filter/);
});
test('all five permitted filter values are accepted on actual scanlines', async () => {
  const scanlines = Buffer.alloc(1601 * 400);
  for (let row = 0; row < 400; row++) scanlines[1601 * row] = row % 5;
  await validateAdAsset('logo', 'image/png', png({ scanlines }));
});
test('indexed, interlaced and non-8-bit PNGs are explicitly unsupported', async () => {
  for (const options of [{ color: 3 }, { interlace: 1 }, { depth: 16 }]) {
    await assert.rejects(validateAdAsset('logo', 'image/png', png(options)), /non-interlaced 8-bit/);
  }
});
test('animation chunks and unsupported critical chunks are rejected', async () => {
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ before: [chunk('acTL', Buffer.alloc(8))] })), /animated/);
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ before: [chunk('ABCD')] })), /critical/);
});
test('nonconsecutive image chunks and trailing bytes are rejected', async () => {
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ after: [chunk('tEXt'), chunk('IDAT')] })), /consecutive/);
  await assert.rejects(validateAdAsset('logo', 'image/png', Buffer.concat([valid, Buffer.from('trailing')])), /trailing/);
});
test('missing end, duplicate header and nonempty end are rejected', async () => {
  await assert.rejects(validateAdAsset('logo', 'image/png', valid.subarray(0, -12)), /missing PNG end/);
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ before: [chunk('IHDR', valid.subarray(16, 29))] })), /duplicate/);
  const source = Buffer.concat([valid.subarray(0, -12), chunk('IEND', Buffer.from('x'))]);
  await assert.rejects(validateAdAsset('logo', 'image/png', source), /invalid PNG end/);
});


test('IDAT bytes after a complete zlib stream are rejected even when CRC is correct', async () => {
  const compressed = deflateSync(Buffer.alloc(1601 * 400));
  for (const suffix of [Buffer.from([0]), Buffer.from('trailing payload'), deflateSync(Buffer.alloc(1601 * 400))]) {
    await assert.rejects(validateAdAsset('logo', 'image/png', png({ imageData: Buffer.concat([compressed, suffix]) })), /trailing PNG compressed/);
  }
});
test('logo PNGs without an alpha channel are rejected while non-logo RGB artwork is supported', async () => {
  for (const color of [0, 2]) await assert.rejects(validateAdAsset('logo', 'image/png', png({ color })), /actual transparency/);
  await validateAdAsset('tool-primary', 'image/png', png({ color: 2, width: 600, height: 600 }));
});
test('an alpha channel alone is insufficient: a fully opaque logo is rejected', async () => {
  const raw = Buffer.alloc(1601 * 400);
  for (let y = 0; y < 400; y++) for (let x = 0; x < 400; x++) raw[y * 1601 + 1 + x * 4 + 3] = 255;
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ scanlines: raw })), /actual transparency/);
  raw[1 + 3] = 254;
  await validateAdAsset('logo', 'image/png', png({ scanlines: raw }));
});
test('invalid tRNS metadata on an alpha PNG is rejected', async () => {
  await assert.rejects(validateAdAsset('logo', 'image/png', png({ before: [chunk('tRNS', Buffer.alloc(6))] })), /transparency chunk/);
});
