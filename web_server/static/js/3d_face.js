import * as THREE from 'https://cdn.jsdelivr.net/npm/three@latest/build/three.module.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@latest/examples/jsm/loaders/GLTFLoader.js';

let scene, camera, renderer, faceModel;

function init() {
    // Scene Setup
    scene = new THREE.Scene();

    // Camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 3;

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('face-container').appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x00ffea, 1.5, 100);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    // Load 3D Model
    const loader = new GLTFLoader();
    loader.load('/static/models/maia_face.glb', (gltf) => {
        faceModel = gltf.scene;
        faceModel.scale.set(1.5, 1.5, 1.5);
        faceModel.position.y = -1;
        scene.add(faceModel);
    }, undefined, (error) => {
        console.error("Error loading model: ", error);
    });

    // Animation
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    if (faceModel) {
        faceModel.rotation.y += 0.01; // Rotate the face model
    }
    renderer.render(scene, camera);
}

// Run
init();
