import { useEffect, useRef } from "react";
import * as THREE from "three";

interface ShaderRippleProps {
  speed?: number;
  lineWidth?: number;
  rippleCount?: number;
  colorLayers?: number;
  backgroundColor?: string;
  rotation?: number;
  timeScale?: number;
  opacity?: number;
  waveIntensity?: number;
  animationSpeed?: number;
  loopDuration?: number;
  scale?: number;
  color1?: string;
  color2?: string;
  color3?: string;
  mod?: number;
  className?: string;
}

export function ShaderRipple({
  speed = 0.05,
  lineWidth = 0.002,
  rippleCount = 8,
  colorLayers = 3,
  backgroundColor = "transparent",
  rotation = 135,
  timeScale = 0.5,
  opacity = 1.0,
  waveIntensity = 0,
  animationSpeed = 1.0,
  loopDuration = 0.7,
  scale = 1,
  color1 = "#10B981",
  color2 = "#10B981",
  color3 = "#34D399",
  mod = 0.2,
  className = "",
}: ShaderRippleProps) {
  const rotationRadians = (rotation * Math.PI) / 180;
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<any>(null);

  const hexToVec3 = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? new THREE.Vector3(
          parseInt(result[1], 16) / 255,
          parseInt(result[2], 16) / 255,
          parseInt(result[3], 16) / 255,
        )
      : new THREE.Vector3(1, 0, 0);
  };

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;

    const vertexShader = `void main(){gl_Position=vec4(position,1.0);}`;
    const fragmentShader = `
      #define TWO_PI 6.2831853072
      #define PI 3.14159265359
      precision highp float;
      uniform vec2 resolution;
      uniform float time;
      uniform float lineWidth;
      uniform int rippleCount;
      uniform int colorLayers;
      uniform float rotation;
      uniform float timeScale;
      uniform float opacity;
      uniform float waveIntensity;
      uniform float scale;
      uniform vec3 color1;
      uniform vec3 color2;
      uniform vec3 color3;
      uniform float loopDuration;
      uniform float modValue;
      vec2 rotate(vec2 v,float a){float s=sin(a);float c=cos(a);return mat2(c,-s,s,c)*v;}
      float easeInOutCubic(float t){return t<0.5?4.0*t*t*t:1.0-pow(-2.0*t+2.0,3.0)/2.0;}
      void main(void){
        vec2 uv=(gl_FragCoord.xy*2.0-resolution.xy)/min(resolution.x,resolution.y);
        uv=uv/scale;
        uv=rotate(uv,rotation);
        uv.x+=sin(uv.y*5.0+time*timeScale*0.1)*waveIntensity;
        uv.y+=cos(uv.x*5.0+time*timeScale*0.1)*waveIntensity;
        float t=mod(time*timeScale*0.05,loopDuration);
        float fadeProgress=t/loopDuration;
        float smoothFade=sin(fadeProgress*PI);
        smoothFade=easeInOutCubic(smoothFade);
        vec3 finalColor=vec3(0.0);
        float totalIntensity=0.0;
        for(int j=0;j<5;j++){
          if(j>=colorLayers)break;
          vec3 layerColor;
          if(j==0)layerColor=color1;
          else if(j==1)layerColor=color2;
          else layerColor=color3;
          float intensity=0.0;
          for(int i=0;i<20;i++){
            if(i>=rippleCount)break;
            float rippleTime=fract(t+float(i)*0.01-0.01*float(j));
            float rippleRadius=rippleTime*rippleTime*8.0;
            intensity+=lineWidth*float(i*i)/abs(rippleRadius-length(uv)+mod(uv.x+uv.y,modValue));
          }
          finalColor+=layerColor*intensity;
          totalIntensity+=intensity;
        }
        if(totalIntensity>0.0){finalColor=finalColor/max(totalIntensity*0.3,1.0);}
        float alpha=min(totalIntensity*0.2,1.0)*opacity*smoothFade;
        gl_FragColor=vec4(finalColor*smoothFade,alpha);
      }
    `;

    const camera = new THREE.Camera();
    camera.position.z = 1;
    const scene = new THREE.Scene();
    const geometry = new THREE.PlaneGeometry(2, 2);
    const uniforms: any = {
      time: { value: 1.0 },
      resolution: { value: new THREE.Vector2() },
      lineWidth: { value: lineWidth },
      rippleCount: { value: rippleCount },
      colorLayers: { value: colorLayers },
      rotation: { value: rotationRadians },
      timeScale: { value: timeScale },
      opacity: { value: opacity },
      waveIntensity: { value: waveIntensity },
      scale: { value: scale },
      color1: { value: hexToVec3(color1) },
      color2: { value: hexToVec3(color2) },
      color3: { value: hexToVec3(color3) },
      loopDuration: { value: loopDuration },
      modValue: { value: mod },
    };
    const material = new THREE.ShaderMaterial({ uniforms, vertexShader, fragmentShader, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false });
    scene.add(new THREE.Mesh(geometry, material));
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);

    const onResize = () => {
      const w = container.clientWidth, h = container.clientHeight;
      renderer.setSize(w, h);
      uniforms.resolution.value.set(renderer.domElement.width, renderer.domElement.height);
    };
    onResize();
    window.addEventListener("resize", onResize);

    let animationId: number;
    const animate = () => {
      animationId = requestAnimationFrame(animate);
      uniforms.time.value += speed * animationSpeed;
      renderer.render(scene, camera);
    };
    sceneRef.current = { renderer, animationId };
    animate();

    return () => {
      window.removeEventListener("resize", onResize);
      cancelAnimationFrame(animationId);
      container.removeChild(renderer.domElement);
      renderer.dispose();
      geometry.dispose();
      material.dispose();
    };
  }, []);

  return <div ref={containerRef} className={`h-full w-full ${className}`} style={{ background: backgroundColor, overflow: "hidden" }} />;
}
