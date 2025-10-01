/*<<crowbar
  from c_func_utils import *
  emit(
      cfunc(
          label="add",
          args=[param("int", "x"), param("int", "y")],
          ret="int",
          body=zebody(),
      ),
  )
>> */
// <<end>>
