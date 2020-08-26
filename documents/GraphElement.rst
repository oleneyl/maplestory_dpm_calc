GraphElement
=============

`dpmModule.core.GraphElement` object는 시뮬레이션의 실행에서 구분되어지는 제일 기본적인 객체입니다. 

GraphElement
------------
``GraphElement`` 기본 객체입니다.
``GraphElement`` Object는 구현 과정에서 반드시 ``_use()`` 메서드를 재정의하여 의도되어야 하는 행동을 정의해야 합니다.

.. autoclass:: dpmModule.kernel.core.GraphElement
  :members:

TaskHolder
------------
.. autoclass:: dpmModule.kernel.core.TaskHolder

OptionalElement
-----------------
.. autoclass:: dpmModule.kernel.core.OptionalElement
