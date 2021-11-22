// Input Medicine 
import React, {useState, useCallback} from 'react';

const InputMedicine = ({onInsert}) => {
    // 변수 모음 
    const [weight,setWeight] = useState(''); //몸무게
    const [wtime,setWtime] = useState(false); // 몸무게 입력 여부
    const [name,setName] = useState(''); //약품명
    const [intake,setIntake] = useState(''); //섭취량

    //사용자 몸무게 입력값 저장
    const onChangeWeight = useCallback(e=>{
        setWeight(e.target.value);
    },[]);
    //사용자 약품명 입력값 저장
    const onChangeName = useCallback(e=>{
        setName(e.target.value);
    },[]);
    //사용자 섭취량 입력값 저장
    const onChangeIntake = useCallback(e=>{
        setIntake(e.target.value);
    },[]);

    // Medicine list를 위해 FormData 생성
    let MediForm = new FormData();
    const onSubmit = useCallback(e=>{
        // Medicine List에 사용자가 입력한 정보 등록
        setWtime(true);
        MediForm.append('weight',weight);
        MediForm.append('name',name); 
        MediForm.append('intake',intake); 

        // Console창 출력
        console.log(weight);
        console.log(name);
        console.log(intake);

        // Medicine List에 등록 및 설정값 초기화
        onInsert(MediForm);
        setName('');
        setIntake('');
        e.preventDefault();
    },[onInsert,MediForm]);

    // HTML form
    // 입력받는 항목은 몸무게, 약품명, 섭취량
    // 몸무게를 한 번 입력하여 약품을 등록한 적이 있으면, 몸무게 input란 변경금지(고정)
    return(
        <form onSubmit={onSubmit}>
            {wtime ? 
            <input type="number" placeholder="몸무게(kg)" value={weight} onChange={onChangeWeight} disabled/>
        :<input type="number" placeholder="몸무게(kg)" value={weight} onChange={onChangeWeight} />}
            <input type="text" placeholder="약품명" value={name} onChange={onChangeName}/>
            <input type="number" placeholder="섭취량" value={intake} onChange={onChangeIntake}/>
            <button type="submit">+</button>
        </form>
    );}

export default InputMedicine;