from nptyping import NDArray
import numpy as np
from copy import deepcopy
from typing import Any, Union
from scipy.spatial.transform import Rotation


def _compose(rotation_matrix: NDArray[(3, 3)], translation_vector: NDArray[(3,)]):
    assert rotation_matrix.shape == (3, 3) and translation_vector.shape == (3,)
    m = np.identity(4)
    m[:3, 3] = np.squeeze(translation_vector)
    m[:3, :3] = rotation_matrix
    return m


class TransformationMatrix(np.ndarray):
    """
    Affine/homogenous transformation matrix (preserves lines in parallelisism)
    Belongs to the special euclidean group SE(3)
    Applies a rotation THEN a translation.
    (not a projection matrix)
    Used to perform rotations and translations in 3D cartesian space (R^3).
    Has 3 uses/interpretations:
        1. Represent configuration/frames
        2. Change reference frame
        3. Displace a vector or frame
    A transformation from frame s to b can be written as T_{sb}.
    Matrices can be composed symbolically as in T_{cb} = T_{cs}T_{sb}.
    A vector can be displaced by a transformation matrix symbolically via v_c=T_{cb}v_b.
    TODO: support sheering and scaling
    """
    def __new__(cls, array=np.identity(4, dtype=np.float32)) -> 'TransformationMatrix':
        if not (array.shape == (4, 4) and np.allclose(array[3, :], [0, 0, 0, 1])):
            raise Exception('Input array is malformed')

        return np.asarray(array).view(cls)

    @staticmethod
    def compose(rotation_matrix: NDArray[(3, 3)], translation: NDArray[3]) -> 'TransformationMatrix':
        return TransformationMatrix(_compose(rotation_matrix, translation))

    @staticmethod
    def from_xyzwpr(xyzwpr: NDArray[6]) -> 'TransformationMatrix':
        xyzwpr = np.array(xyzwpr)
        return TransformationMatrix.compose(
            Rotation.from_euler('xyz', xyzwpr[3:], degrees=True).as_matrix(),
            xyzwpr[:3]
        )

    @staticmethod
    def make_random(rotation_bounds, translation_bounds) -> 'TransformationMatrix':
        import numbers

        def preprocess(bounds):
            if isinstance(bounds, numbers.Number):
                bounds = np.ones(3) * bounds
            bounds = np.array(bounds)
            if len(bounds.shape) == 1:
                bounds = np.hstack([
                    -bounds.reshape(-1, 1),
                    bounds.reshape(-1, 1)])
            return bounds

        def box_uniform(bounds):
            return np.array([np.random.uniform(low, hgh) for low, hgh in bounds])

        translation_bounds = preprocess(translation_bounds)
        rotation_bounds = preprocess(rotation_bounds)
        translation = box_uniform(translation_bounds)
        rotation = box_uniform(rotation_bounds)
        return TransformationMatrix.from_xyzwpr(
            np.concatenate([translation, rotation])
        )

    @property
    def rotation(self) -> Rotation:
        return Rotation.from_matrix(self.rotation_matrix)

    @property
    def rotation_matrix(self) -> NDArray[(3, 3)]:
        return np.array(self)[:3, :3]

    @property
    def rotation_euler(self) -> NDArray[3]:
        # degrees about xyz (extrinsic)
        return self.rotation.as_euler('xyz', degrees=True)

    @property
    def translation(self) -> NDArray[3]:
        return np.array(self)[:3, 3]

    @property
    def inv(self) -> 'TransformationMatrix':
        # faster inverse using property of transformation matrix
        arr = deepcopy(self)
        t = arr.rotation_matrix.T
        arr[:3, :3] = t
        arr[:3, 3] = -t @ arr.translation
        return arr

    def transform(self, x: Union[NDArray[(3, Any)], NDArray[3]]) -> NDArray[(3, Any)]:
        if len(x.shape) == 1:
            x = x[:, np.newaxis]
        x = np.vstack([x, np.ones(x.shape[1])])
        return (self @ x)[:3, :]

    def __str__(self):
        if (not self.shape[0] == 4 and self.shape[1] == 4):
            # trying to print a subarray, ie "print(transform[:3])"
            return np.array(self)
        return 'x={0}, y={1}, z={2}\nx_rotate={3}°, y_rotate={4}°, z_rotate={5}°'\
            .format(*self.translation.round(2), *self.rotation_euler.round(2))


if __name__ == '__main__':
    arr = TransformationMatrix()
    assert np.allclose(arr, np.identity(4))
    assert np.allclose(arr.translation, np.zeros(3))
    assert np.allclose(arr.rotation_matrix, np.identity(3))
    assert isinstance(arr.inv, TransformationMatrix)
    assert np.allclose(arr.inv, np.identity(4))
    arr2 = TransformationMatrix.from_xyzwpr([0, 1, 0, 90, 0, 0])
    assert np.allclose(arr2.rotation_matrix,
                       [[1,  0,  0, ],
                        [0,  0, -1, ],
                           [0,  1,  0, ]])
    assert np.allclose(arr2.translation, [0, 1, 0])
    v = np.array([0, 1, 0])
    assert np.allclose(arr2.transform(v).T, [[0, 1, 1]])
    arr3 = TransformationMatrix.compose(np.identity(3), np.zeros(3))
    assert np.allclose(arr3, np.identity(4))
    arr4 = TransformationMatrix().make_random(40, 40)
    print(arr4)
