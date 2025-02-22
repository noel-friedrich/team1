interface WikiLogoProps {
  letter: string;
}

export default function WikiLogo({ letter }: WikiLogoProps) {
  return (
    <div className="w-36 h-36 rounded-full bg-[#f8f9fa] border-4 border-[#a2a9b1] flex items-center justify-center">
      <span className="text-7xl font-serif text-[#202122]">{letter}</span>
    </div>
  );
}
  
  