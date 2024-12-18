/*import * as THREE from 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.module.min.js';
import { GLTFLoader } from 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/examples/jsm/loaders/GLTFLoader.js';

let scene, camera, renderer, faceModel;

function init() {
    // Set up scene, camera, and renderer
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);

    // Attach to the face container
    const faceContainer = document.getElementById('face-container');
    faceContainer.appendChild(renderer.domElement);

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0x00ffff, 1.5); // Glowing light
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1.2, 100);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    // Load the 3D face model
    const loader = new GLTFLoader();
    loader.load('/static/models/maia_face.glb', (gltf) => {
        faceModel = gltf.scene;
        faceModel.scale.set(2, 2, 2);
        faceModel.position.set(0, -1, 0);
        scene.add(faceModel);
    }, undefined, (error) => {
        console.error("Error loading model: ", error);
    });

    // Position camera
    camera.position.z = 5;

    // Start animation
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    if (faceModel) {
        faceModel.rotation.y += 0.01; // Rotate the face
    }
    renderer.render(scene, camera);
}

// Initialize
init();
*/