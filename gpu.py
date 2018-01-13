import pycuda.autoinit
import pycuda.driver as drv
import numpy as np

from pycuda.compiler import SourceModule

class CudaSys():
    def __init__(self):
        self.device = None


if __name__ == '__main__':

    a1 = np.random.randn(1,4).astype(np.float32)
    a2 = np.random.randn(1,4).astype(np.float32)
    o1 = np.zeros((1,4)).astype(np.float32)

    a1_gpu = drv.mem_alloc(a1.nbytes)
    a2_gpu = drv.mem_alloc(a2.nbytes)
    o1_gpu = drv.mem_alloc(o1.nbytes)

    drv.memcpy_htod(a1_gpu, a1)
    drv.memcpy_htod(a2_gpu, a2)
    drv.memcpy_htod(o1_gpu, o1)
    
    mod = SourceModule(
    """
    __global__ void do_something(float *A1, float *A2, float *O1){
        O1[threadId.x] = A1[threadId.x]*A2[threadId.y]
    }

    """)

    foo = mod.get_function("do_something")
    foo(a_gpu, a2_gpu, o1_gpu, block=(4,4,1))

    print(a1)
    print(a2)
    print(o1)
