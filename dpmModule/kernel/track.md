- Graph building seqeunce

  - First, learn about the process of creating GraphElement. GraphElement is created through the following process. 먼저 GraphElement를 생성하는 과정에 대해 알아봅니다. GraphElement는 다음과 같은 과정을 거쳐 생성됩니다.
     
    It is recommended to go through the following process for most GraphElements. It is recommended to use the following instead of the usual graph elements. 대부분의 GraphElement는 다음과 같은 과정을 거치는 것이 추천됩니다. 일반적인 그래프요소 대신 다음을 사용하는 것이 권장됩니다.

    - Use TrackableGraphElement(). TrackableGraphElement() 를 사용합니다.

    
    - Create GraphElementPrecursor() first. GraphElementPrecursor()를 먼저 생성합니다.
    - Call GraphElementPrecursor.transfer_into_real() to switch to the actual graph element at build time. GraphElementPrecursor.transfer_into_real()을 호출하여 실제 그래프 요소로 빌드 타임에 전환됩니다.

    GraphElementPrecursor is | GraphElementPrecursor는 


- Precursor handling

  The most differentiated part between the previous DpmModule and the current DpmModule is the provision of Precursor Variables. By introducing Precursor Variable, the following features
  Came into being. 이전 DpmModule과 현재의 DpmModule이 제일 차별화되는 부분은 Precursor Variable의 제공입니다. Precursor Variable을 도입함으로서 다음과 같은 특징이
  생겨났습니다.

  - You can modify the information based on the storage in the graph. Graph에 Storage를 기반으로 정보를 수정할 수 있습니다. 
  - All constants applied to the graph can be saved as XML / JSON. Graph에 적용되고 있는 모든 상수를 XML / JSON으로 저장할 수 있습니다.
  - You can easily check the graph settings. Graph의 설정을 손쉽게 확인할 수 있습니다.


  -DynamicVariable. DynamicVariable is a dynamic variable element that can get the actual value through evaluate(). However, this Framework directly
    It is not recommended to create it. As a substitute for that, let DynamicVriableOperation automatically cast the variable. Apart from this, it is necessary to allocate variable space
    It is recommended to form a Bone class object directly on the present element.

  -DynamicObject. DynamicObject is an element that can have DynamicVariable as Object propery. `All VariableObjects are automatically tracked by the graph`.
    All created DynamicObjects can call the internal scope and convert the declared variable within the calling scope into a real variable at build time. Tracking targets of all VariableObjects are automatically replaced with actual values ​​at build time. revert is also possible.

  However, by introducing the Precursor, the evaluation point of the variable will be different from the build point of the graph, which can make the control of the graph more complex.
  To prevent this, use DynamicVariable in compliance with the following rules. 그러나 Precursor를 도입함으로서, Variable의 Evaluation 시점이 Graph의 빌드 시점과 달라지게 되고 이로 인해 Graph의 Control이 좀 더 복잡해질 수 있습니다.
  이를 방지하기 위해, 아래와 같은 Rule을 준수하여 DynamicVariable을 사용해 주십시오.

  - DynamicVariable: DynamicVariable is a dynamic variable element that can get actual value through evaluate() However, this Framework does not recommend creating this class object directly. 
    As a replacement for that, let DynamicVriableOperation automatically cast variables. Apart from this, it is recommended to form this class object directly for elements that need to allocate variable space. 
    DynamicVariable은 evaluate()를 통해 실제 값을 얻어올 수 있는 동적 변수요소입니다. 그러나, 본 Framework는 이 클래스 오브젝트를 직접적으로 생성하는것을 권장하지 않습니다. 그에 대한 대체제로, DynamicVriableOperation이 
    자동으로 변수를 cast하도록 하십시오. 이와는 별개로, 변수공간을 할당할 필요가 있는 요소에는 직접적으로 본 클래스 오브젝트를 형성하는것이 추천됩니다.

  - DynamicObject: DynamicObject is an element that can have DynamicVariable as Object propery. `All VariableObjects are automatically tracked by the graph`. All created DynamicObjects can call the 
    internal scope and convert the declared variable within the calling scope into a real variable at build time. Tracking targets of all VariableObjects are automatically replaced with actual values at build time. revert is also possible. 
    DynamicObject는 Object propery로 DynamicVariable을 가질 수 있는 요소입니다. `모든 VariableObject는 그래프에 의해 자동으로 추적됩니다`. 모든 생성된 DynamicObject는 내부 scope를 호출하여 호출 scope 이내에 선언된 변수를 빌드 시점에 실변수로 전환할 수 있습니다. 
    모든 VariableObject의 추척 대상은 빌드 시점에서 자동으로 실제값으로 치환됩니다. revert또한 가능합니다.