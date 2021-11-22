import React, { useState, useRef, useCallback } from 'react';
import {Link, Route} from 'react-router-dom';
import '../index.css';
import InputMedicine from './InputMedicine';
import InputMedicineList from './InputMedicineList';
import axios from 'axios';

//메인페이지(단일 사용자 입력 페이지)
const Main = ()=>{
  const nextId = useRef(1);
  const [medicines,setMedicines] = useState([]); //입력으로 들어온 건강기능식품의 배열
  const [heavy,setHeavy] = useState([]); //중금속 성분만 담은 배열
  const [output,setOutput] = useState([]); //전체 성분을 담은 배열
  const [list,setList] = useState([]); //실제 보여지는 성분들의 배열
  const [checked,setCheck] = useState(false); //중금속만 보여주기 여부
  const [title,setTitle] = useState(""); //중금속만 보기/전체보기 버튼의 글씨

  const onInsert = useCallback(
    data => {
      const medicine = {
        id:nextId.current,
        weight: data.get('weight'),
        name: data.get('name'),
        intake: data.get('intake')
  };
  setMedicines(medicines.concat(medicine));
  nextId.current += 1;
},[medicines]);

const onClick = async() => { //입력값을 post하여 반환값을 배열에 저장
  await axios.post("http://localhost:5000/api/sendintake",{data:medicines}).then(
      async response=>{
        setHeavy(response.data.data.intake.filter(intake_element => intake_element.isHeavyMetal===true));       
        setOutput(response.data.data.intake); 
        setList(response.data.data.intake);
        setTitle("중금속만 보기");
      })
}
const heavy_button = () => { //중금속만 보기 여부를 선택하는 버튼
  if(!checked){
    setList(heavy);
    setCheck(true);
    setTitle("전체 보기");
  }else{
    setList(output);
    setCheck(false);
    setTitle("중금속만 보기");
  }
}
  return (
    <div>
      <div className="header">
        <h1>건강기능식품 프로젝트</h1>
        <Link to = '/file'><span className="usermode">(단일)사용자 직접 입력</span></Link> 
      </div>
      <div className="body">
        <div className="form">
          <InputMedicine onInsert={onInsert}/>
        <button className="sendBtn" onClick={onClick}>총 성분 섭취량 구하기</button>
        <button className="heavyBtn" onClick={heavy_button}>{title}</button>
        </div>
        <div className="input">
          <h3>Input</h3><InputMedicineList medicines={medicines}/>
        </div>
        <div className="output">
          <h3>Output</h3>
          {list.map(intake_element => (
                <div key={intake_element.word_id} className="medicine-">
                    <li>{intake_element.word_name} {(Math.round(intake_element.volume*1000)/1000).toFixed(3)} {intake_element.unit} 
                    {intake_element.percentage===0 ? <p/> : ' ('+(Math.round(intake_element.percentage*1000)/1000).toFixed(3)+'%)'}</li>
                </div>
            ))}
        </div>  
      </div>
    </div>
  );
}

export default Main;