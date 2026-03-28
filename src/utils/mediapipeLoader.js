const loaderState = {
  handsCtorPromise: null,
  cameraCtorPromise: null
}

function readGlobalCtor(name) {
  const ctor = globalThis?.[name]
  if (typeof ctor !== 'function') {
    throw new Error(`${name} 构造器加载失败`)
  }
  return ctor
}

async function loadWithCache(stateKey, loadModule, globalName) {
  if (!loaderState[stateKey]) {
    loaderState[stateKey] = loadModule()
      .then(() => readGlobalCtor(globalName))
      .catch(error => {
        loaderState[stateKey] = null
        throw error
      })
  }

  return loaderState[stateKey]
}

export function loadHandsCtor() {
  return loadWithCache(
    'handsCtorPromise',
    () => import('@mediapipe/hands/hands.js'),
    'Hands'
  )
}

export function loadCameraCtor() {
  return loadWithCache(
    'cameraCtorPromise',
    () => import('@mediapipe/camera_utils/camera_utils.js'),
    'Camera'
  )
}
