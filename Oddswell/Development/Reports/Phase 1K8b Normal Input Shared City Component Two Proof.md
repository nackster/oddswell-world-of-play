# Phase 1K.8b Normal Input Shared City Component-Two Proof

## Outcome

**COMPLETE - NORMAL INPUT, SHARED MEMBERSHIP, MUTUAL VISIBILITY, STARTER APPEARANCE, AND REPLICATED MOVEMENT PASSED.**

A fresh no-QA owner used the approved non-default chooser path, joined the already-running machine-local Sundale peer, and completed the remaining technical evidence for component 2. The peer reached `clients=2`, both packaged windows visibly showed the other player, the peer showed the selected tan preset in the approved off-white starter clothing, and a normal Shift+A movement control produced a visible replicated position change.

This is a packaged technical proof. It is not an observed first-time-player usability result, external-network proof, beta-readiness claim, or production-readiness claim.

## Scope advanced

- Roadmap: Phase 1K - First-hour vertical slice, component 2.
- Beta Game Bible: `First-hour player journey` - `2. Enter the first city`.
- Player-facing risk reduced: a player can now follow the normal chooser into the same Sundale session as another player, see the other avatar, preserve the selected starter appearance, and replicate movement.

## Supported control-path recovery

The earlier fail-fast attempt was blocked by `node_repl exec context not found`. The failure was not an OddsWell or Unreal defect. `@oai/sky` module and window objects had been reused across separate Node REPL executions, but the privileged bridge validates the active execution identity.

The supported recovery was:

1. reset the Node REPL kernel;
2. import `@oai/sky` inside the same execution that lists and selects the returned Windows target;
3. observe and act on that fresh window object without carrying it into a later execution;
4. reset before the next independent Computer Use transaction.

No Codex configuration, Windows setting, PowerShell UI automation, game code, package, dependency, or hidden input path changed.

## Fresh packaged proof

- Evidence root: `C:\tmp\OddsWellPhase1K8bUnblocked-20260806T200311Z`
- The isolated owner and peer profiles remain retained under that evidence root for audit; neither is a normal-player or active launch path.
- Package: unchanged Phase 1K.8a Windows Development package.
- Game executable: `C:\tmp\OddsWellPhase1K8Package-20260806T035603Z\Windows\OddsWell\Binaries\Win64\OddsWell.exe`
- Passive peer: PID `34148`, window `265194`, isolated profile, `/Game/Maps/SundaleGraybox?listen`, gameplay `-multihome=127.0.0.1 -port=17777`.
- Owner: PID `11416`, window `199778`, fresh isolated profile, normal package start, no map URL, QA flag, chooser driver, preloaded save, or hidden shortcut.
- Peer input count: `0`.

The normal player path was:

1. Computer Use observed the eight-card production chooser.
2. `Right` selected non-default `masculine_tone_2`.
3. physical Enter (`Return` keysym) confirmed exactly once.
4. The owner emitted one production appearance save and client-traveled to `127.0.0.1:17777`.
5. The peer emitted `ODDSWELL_SHARED_CITY_JOIN|clients=2|boundary=local_listen_server`.
6. The peer accepted `masculine_tone_2`, `starter_offwhite_top`, and `starter_offwhite_bottom` from the owner's client RPC.
7. The owner window visibly showed `Player 1`; the peer window visibly showed `Player 1` and `Player 2` together with distinct light and tan skin tones and the same off-white starter clothing.
8. After an ordinary viewport-focus click, normal Shift+A input moved Player 2. Before/after peer observations showed Player 2 change position while Player 1 and the surrounding collision geometry remained fixed.
9. Both clients closed through normal Alt+F4 input. No OddsWell process or gameplay UDP `17777` endpoint remained.

Unfocused W/S/D taps made no visible movement and caused no authority mutation. They are retained as input-focus diagnostics, not counted as movement proof. The successful movement evidence uses only the existing normal locomotion control after the game viewport received focus.

## Authoritative evidence

- Owner save: `ODDSWELL_APPEARANCE_SAVE|result=PASS|schema=1|preset=masculine_tone_2|top=starter_offwhite_top|bottom=starter_offwhite_bottom|slot=production|confirmed_once=true`.
- Owner handoff: `ODDSWELL_CHARACTER_HANDOFF|result=START|target=127.0.0.1:17777|mode=client_travel|boundary=machine_local_development`.
- Peer membership: `ODDSWELL_SHARED_CITY_JOIN|clients=2|boundary=local_listen_server`.
- Peer appearance: `ODDSWELL_SHARED_CITY_APPEARANCE_ACCEPTED|player=2|preset=masculine_tone_2|top=starter_offwhite_top|bottom=starter_offwhite_bottom|owner_submitted=true|source=client_rpc`.
- Peer game socket: `Created socket for bind address: 127.0.0.1:17777`.
- Travel/fatal/assert/ensure matches: `0`.

Retained hashes:

- `Owner.log`: `13554598D45A98249F83F7D806D225E26B9C03CD1A30E14A8ABB81C1C72405EE`
- `Peer.log`: `B21C0610372BB4D891768310C0F15848DE19690D4F579E3377778A29A7B122CE`
- Owner appearance SaveGame captured during evidence retention: `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98`, `2,183` bytes, mtime `2026-08-06T20:03:53.4525490Z`.
- Game executable: `F4BA693DF3CD125689528B7298517096E1E8E053FF439136FDBD9A485EC03E54`.

## Verification boundary

No source or package changed, so the completed Phase 1K.8a editor build, focused native `1/1`, full native `49/49`, frozen Python `105/105`, Brain Admin `--check`, BuildCookRun, and package audit remain the applicable build evidence; no no-op rebuild was performed.

Component 1 and component 2 now have fresh packaged technical proof. Components 3-8 remain **NOT REACHED** in the contiguous first-hour route. The run did not discover locations, enter the Studio, work, open wagering, watch or skip a game, settle a wager, buy or equip an item, or cross a cold persistence boundary.

## Next gate

Phase 1K.9 should use fresh isolated owner and passive-peer profiles, repeat the completed components 1-2, and measure only component 3: discover the required Sundale locations through normal movement, enter and move inside the empty Studio, exit to the exact doorway, and stop before the job interaction in component 4.
