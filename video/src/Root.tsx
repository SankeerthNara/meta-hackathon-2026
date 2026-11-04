import React from "react";
import { Composition, Still, staticFile } from "remotion";
import { getAudioDurationInSeconds } from "@remotion/media-utils";
import { Main, FPS } from "./Main";
import { Thumbnail } from "./Thumbnail";

export const Root: React.FC = () => (
  <>
  <Still id="Thumbnail" component={Thumbnail} width={1920} height={1080} />
  <Composition
    id="Main"
    component={Main}
    fps={FPS}
    width={1920}
    height={1080}
    durationInFrames={FPS * 180}
    calculateMetadata={async () => ({
      // video length follows the ElevenLabs narration, plus a 2 s tail on the title card
      durationInFrames: Math.ceil((await getAudioDurationInSeconds(staticFile("narration.mp3")) + 2) * FPS),
    })}
  />
  </>
);
